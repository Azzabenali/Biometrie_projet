# serveur/database.py
import sqlite3
import logging
from datetime import datetime
from serveur.config import Config

logger = logging.getLogger(__name__)

def get_connection():
    """Retourne une connexion à la base SQLite."""
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row  # Accès par nom de colonne
    return conn

def init_db():
    """Initialise les tables si elles n'existent pas."""
    conn = get_connection()
    cursor = conn.cursor()

    # Table utilisateurs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            is_active INTEGER DEFAULT 1
        )
    """)

    # Table fragments serveur (fragment B chiffré)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fragments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            fragment_b_encrypted TEXT NOT NULL,  -- JSON base64
            fragment_b_hash TEXT NOT NULL,        -- SHA-256 pour intégrité
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # Table logs d'authentification (exigence ISO 27001 A.12)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auth_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            action TEXT NOT NULL,        -- 'enroll', 'auth_success', 'auth_fail'
            timestamp TEXT NOT NULL,
            ip_address TEXT,
            details TEXT                 -- JSON optionnel
        )
    """)

    conn.commit()
    conn.close()
    logger.info("Base de données initialisée.")

def save_fragment(user_id: str, fragment_b_encrypted: str, fragment_b_hash: str):
    """Enregistre ou met à jour le fragment B d'un utilisateur."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()

    # Upsert utilisateur
    cursor.execute("""
        INSERT OR IGNORE INTO users (user_id, created_at)
        VALUES (?, ?)
    """, (user_id, now))

    # Upsert fragment
    cursor.execute("""
        INSERT INTO fragments (user_id, fragment_b_encrypted, fragment_b_hash, created_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            fragment_b_encrypted = excluded.fragment_b_encrypted,
            fragment_b_hash = excluded.fragment_b_hash,
            created_at = excluded.created_at
    """, (user_id, fragment_b_encrypted, fragment_b_hash, now))

    conn.commit()
    conn.close()

def get_fragment(user_id: str) -> dict | None:
    """Récupère le fragment B chiffré d'un utilisateur."""
    conn = get_connection()
    cursor = conn.cursor()
    row = cursor.execute("""
        SELECT fragment_b_encrypted, fragment_b_hash
        FROM fragments WHERE user_id = ?
    """, (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def log_action(user_id: str, action: str, ip_address: str = None, details: str = None):
    """Journalise une action (enrôlement, auth réussie/échouée)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO auth_logs (user_id, action, timestamp, ip_address, details)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, action, datetime.utcnow().isoformat(), ip_address, details))
    conn.commit()
    conn.close()

def delete_user(user_id: str):
    """Supprime toutes les données d'un utilisateur (droit à l'oubli ISO 27018)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fragments WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    logger.info(f"Données supprimées pour {user_id} (droit à l'oubli).")