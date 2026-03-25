# serveur/api.py
import json
import logging
import hashlib
import time
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import Flask, request, jsonify, g

from serveur.config import Config
from serveur.database import init_db, save_fragment, get_fragment, log_action
from serveur.crypto_serveur import encrypt, decrypt  # ← Module Étudiant 2

# ─── Configuration du logging ───────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# ─── Application Flask ───────────────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object(Config)




# ─── Utilitaire JWT ──────────────────────────────────────────────────────────
def generate_token(user_id: str) -> str:
    """Génère un token JWT signé avec expiration."""
    payload = {
        "sub": user_id,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(
            minutes=Config.JWT_EXPIRATION_MINUTES
        )
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")

def require_jwt(f):
    """Décorateur : vérifie le token JWT dans l'en-tête Authorization."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token manquant"}), 401
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(
                token, Config.JWT_SECRET_KEY, algorithms=["HS256"]
            )
            g.current_user = payload["sub"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expiré"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token invalide"}), 401
        return f(*args, **kwargs)
    return decorated


# ─── ROUTE 1 : Health check ──────────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()})


# ─── ROUTE 2 : Enrôlement ────────────────────────────────────────────────────
@app.route("/enroll", methods=["POST"])
def enroll():
    """
    Corps attendu (JSON) :
    {
        "user_id": "alice",
        "fragment_b": [0.45, 0.12, ..., 0.87]  // liste de 64 floats
    }
    """
    start_time = time.time()
    data = request.get_json()

    # Validation des champs
    if not data or "user_id" not in data or "fragment_b" not in data:
        return jsonify({"error": "Champs manquants : user_id, fragment_b"}), 400

    user_id = str(data["user_id"]).strip()
    fragment_b = data["fragment_b"]

    if not isinstance(fragment_b, list) or len(fragment_b) != 64:
        return jsonify({"error": "fragment_b doit être une liste de 64 floats"}), 400

    # Sérialisation du fragment en JSON bytes
    fragment_bytes = json.dumps(fragment_b).encode("utf-8")

    # Hash SHA-256 pour vérifier l'intégrité plus tard
    fragment_hash = hashlib.sha256(fragment_bytes).hexdigest()

    # Chiffrement AES-256 GCM (Étudiant 2)
    aes_key = bytes.fromhex(Config.SERVER_AES_KEY)
    fragment_encrypted = encrypt(fragment_bytes, aes_key)  # retourne str base64

    # Stockage en base
    save_fragment(user_id, fragment_encrypted, fragment_hash)

    # Journalisation
    log_action(user_id, "enroll", request.remote_addr)

    elapsed = round((time.time() - start_time) * 1000, 2)
    logger.info(f"[ENROLL] user={user_id} | durée={elapsed}ms")

    return jsonify({
        "status": "enrolled",
        "user_id": user_id,
        "duration_ms": elapsed
    }), 201


# ─── ROUTE 3 : Récupération du fragment B (pour authentification) ────────────
@app.route("/fragment/<user_id>", methods=["GET"])
@require_jwt
def get_fragment_route(user_id: str):
    """
    Retourne le fragment B chiffré au client authentifié (JWT requis).
    Le client déchiffrera côté client avec sa clé.
    """
    # Sécurité : un utilisateur ne peut récupérer QUE son propre fragment
    if g.current_user != user_id:
        return jsonify({"error": "Accès interdit"}), 403

    row = get_fragment(user_id)
    if not row:
        return jsonify({"error": "Utilisateur non trouvé"}), 404

    return jsonify({
        "user_id": user_id,
        "fragment_b_encrypted": row["fragment_b_encrypted"],
        "fragment_b_hash": row["fragment_b_hash"]
    })


# ─── ROUTE 4 : Authentification ──────────────────────────────────────────────
@app.route("/authenticate", methods=["POST"])
def authenticate():
    """
    Corps attendu (JSON) :
    {
        "user_id": "alice",
        "auth_result": true/false,   // résultat calculé CÔTÉ CLIENT
        "score": 0.08                // distance cosinus (optionnel, pour logs)
    }
    Le client a déjà recombiné les fragments et effectué la comparaison.
    Le serveur valide et émet un JWT si succès.
    """
    start_time = time.time()
    data = request.get_json()

    if not data or "user_id" not in data or "auth_result" not in data:
        return jsonify({"error": "Champs manquants"}), 400

    user_id = str(data["user_id"]).strip()
    auth_result = bool(data["auth_result"])
    score = data.get("score", None)

    # Vérifier que l'utilisateur existe
    row = get_fragment(user_id)
    if not row:
        return jsonify({"error": "Utilisateur non enrôlé"}), 404

    elapsed = round((time.time() - start_time) * 1000, 2)

    if auth_result:
        token = generate_token(user_id)
        log_action(
            user_id, "auth_success", request.remote_addr,
            json.dumps({"score": score, "duration_ms": elapsed})
        )
        logger.info(f"[AUTH SUCCESS] user={user_id} | score={score} | {elapsed}ms")
        return jsonify({
            "status": "authenticated",
            "user_id": user_id,
            "token": token,
            "duration_ms": elapsed
        })
    else:
        log_action(
            user_id, "auth_fail", request.remote_addr,
            json.dumps({"score": score})
        )
        logger.warning(f"[AUTH FAIL] user={user_id} | score={score}")
        return jsonify({"status": "rejected", "reason": "Score biométrique insuffisant"}), 401


# ─── ROUTE 5 : Suppression (droit à l'oubli ISO 27018) ───────────────────────
@app.route("/user/<user_id>", methods=["DELETE"])
@require_jwt
def delete_user_route(user_id: str):
    if g.current_user != user_id:
        return jsonify({"error": "Accès interdit"}), 403
    from serveur.database import delete_user
    delete_user(user_id)
    log_action(user_id, "delete", request.remote_addr)
    return jsonify({"status": "deleted", "user_id": user_id})

# ─── Lancement du serveur ─────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    app.run(
        host="0.0.0.0",
        port=5443,
        ssl_context=(Config.CERT_PATH, Config.KEY_PATH),
        debug=False
    )