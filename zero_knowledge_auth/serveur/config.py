import os
import secrets

class Config:
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", secrets.token_hex(32))
    JWT_EXPIRATION_MINUTES = 30
    SERVER_AES_KEY = "a3f8c2e1d4b7a9f0e2c5d8b1a4f7c0e3d6b9a2f5c8e1d4b7a0f3c6e9d2b5a8f1"
    DB_PATH = "zero_knowledge_auth/serveur/zero_knowledge.db"
    CERT_PATH = "zero_knowledge_auth/serveur/certs/cert.pem"
    KEY_PATH  = "zero_knowledge_auth/serveur/certs/key.pem"
    AUTH_THRESHOLD = 0.15