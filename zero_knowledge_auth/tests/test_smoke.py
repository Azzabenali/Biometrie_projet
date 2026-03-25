import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def test_numpy():
    import numpy as np
    arr = np.random.default_rng(42).random(128)
    assert len(arr) == 128
    assert all(0.0 <= v <= 1.0 for v in arr)

def test_jwt():
    import jwt
    key = "s" * 32  # 32 bytes minimum pour SHA256
    token = jwt.encode({"sub": "alice", "exp": 9999999999}, key, algorithm="HS256")
    decoded = jwt.decode(token, key, algorithms=["HS256"]) 
    assert decoded["sub"] == "alice"

def test_aes_gcm():
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    import os
    key = os.urandom(32)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, b"biometrie zero knowledge", b"")
    pt = aesgcm.decrypt(nonce, ct, b"")
    assert pt == b"biometrie zero knowledge"

def test_capture():
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from client.capture import capture_biometric_template
    t = capture_biometric_template("test_user")
    assert len(t) == 128
    assert all(isinstance(v, float) for v in t)

def test_flask_health():
    from serveur.api import app
    client = app.test_client()
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"