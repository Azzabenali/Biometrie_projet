from cryptography.fernet import Fernet
import os

def generate_and_save_key(key_path="secret.key"):
    """
    Génère une clé de chiffrement AES et la sauvegarde dans un fichier.
    """
    # Génération de la clé
    key = Fernet.generate_key()
    
    # Sauvegarde de la clé dans un fichier local
    with open(key_path, "wb") as key_file:
        key_file.write(key)
    
    print(f"SUCCÈS : Clé de chiffrement générée et sauvegardée dans : {key_path}")
    print("ATTENTION : Ne perdez pas ce fichier, sinon vous ne pourrez plus lire vos templates !")

if __name__ == "__main__":
    generate_and_save_key()
