import os
import json
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt(data: bytes, key: bytes) -> str:
    """
    Chiffre des données avec AES-256 GCM.
    Retourne une chaîne base64 : nonce (12 bytes) + ciphertext.
    """
    if len(key) != 32:
        raise ValueError(f"Clé AES-256 doit faire 32 bytes, reçu {len(key)}")
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, data, b"zero-knowledge-auth")
    combined = nonce + ciphertext
    return base64.b64encode(combined).decode("utf-8")

def decrypt(encrypted_b64: str, key: bytes) -> bytes:
    """
    Déchiffre une chaîne base64 produite par encrypt().
    Retourne les données originales en bytes.
    """
    if len(key) != 32:
        raise ValueError(f"Clé AES-256 doit faire 32 bytes, reçu {len(key)}")
    combined = base64.b64decode(encrypted_b64.encode("utf-8"))
    nonce = combined[:12]
    ciphertext = combined[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, b"zero-knowledge-auth")

def encrypt_fragment(fragment: list, key: bytes) -> str:
    """Chiffre une liste de floats (fragment biométrique)."""
    data = json.dumps(fragment).encode("utf-8")
    return encrypt(data, key)

def decrypt_fragment(encrypted_b64: str, key: bytes) -> list:
    """Déchiffre et retourne une liste de floats."""
    data = decrypt(encrypted_b64, key)
    return json.loads(data.decode("utf-8"))

if __name__ == "__main__":
    key = os.urandom(32)
    fragment = [round(i * 0.01, 4) for i in range(64)]
    enc = encrypt_fragment(fragment, key)
    dec = decrypt_fragment(enc, key)
    assert fragment == dec, "Erreur : fragment modifié après chiffrement/déchiffrement"
    print("[CRYPTO] Test AES-256 GCM : OK")
    print(f"Fragment original  : {fragment[:3]}...")
    print(f"Fragment chiffré   : {enc[:40]}...")
    print(f"Fragment déchiffré : {dec[:3]}...")