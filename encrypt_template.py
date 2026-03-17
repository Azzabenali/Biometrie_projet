from cryptography.fernet import Fernet
import os

def encrypt_file(input_file="template.json", output_file="template.enc", key_path="secret.key"):
    """
    Lit le template JSON, le chiffre avec la clé secrète et sauvegarde le résultat.
    """
    # 1. Charger la clé secrète générée à l'étape 1
    if not os.path.exists(key_path):
        print(f"Erreur : La clé {key_path} est introuvable. Relancez l'étape 1.")
        return
    
    with open(key_path, "rb") as key_file:
        key = key_file.read()
    
    cipher_suite = Fernet(key)

    # 2. Lire le contenu du fichier template.json
    if not os.path.exists(input_file):
        print(f"Erreur : Le fichier {input_file} est introuvable.")
        return

    with open(input_file, "rb") as f:
        file_data = f.read()

    # 3. Chiffrer les données
    encrypted_data = cipher_suite.encrypt(file_data)

    # 4. Sauvegarder le fichier chiffré
    with open(output_file, "wb") as f:
        f.write(encrypted_data)

    print(f"SUCCÈS : Le fichier '{input_file}' a été chiffré et sauvegardé sous '{output_file}'.")
    print("Vous pouvez maintenant essayer d'ouvrir 'template.enc' avec le Bloc-notes : il sera illisible !")

if __name__ == "__main__":
    encrypt_file()
