import hashlib
from cryptography.fernet import Fernet
import os
import json

def verify_and_decrypt(enc_file="template.enc", hash_file="template.hash", key_path="secret.key"):
    """
    Vérifie l'intégrité du fichier chiffré, puis le déchiffre.
    """
    # 1. Vérification de l'intégrité (Hash)
    with open(enc_file, "rb") as f:
        current_data = f.read()
    
    current_hash = hashlib.sha256(current_data).hexdigest()
    
    with open(hash_file, "r") as f:
        saved_hash = f.read().strip()
    
    if current_hash != saved_hash:
        print("ALERTE : L'intégrité du fichier est compromise ! Le fichier a été modifié.")
        return
    else:
        print("SUCCÈS : L'intégrité du fichier est vérifiée (Hash OK).")

    # 2. Déchiffrement
    with open(key_path, "rb") as f:
        key = f.read()
    
    cipher_suite = Fernet(key)
    decrypted_data = cipher_suite.decrypt(current_data)
    
    # 3. Conversion en JSON pour vérification
    template_data = json.loads(decrypted_data)
    
    print(f"SUCCÈS : Données déchiffrées pour l'utilisateur : {template_data['user_id']}")
    print(f"Nombre de caractéristiques extraites : {len(template_data['features'])}")
    print("\n--- SYSTÈME DE SÉCURITÉ BIOMÉTRIQUE OPÉRATIONNEL ---")

if __name__ == "__main__":
    verify_and_decrypt()
