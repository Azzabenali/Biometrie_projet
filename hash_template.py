import hashlib
import os

def calculate_and_save_hash(file_path="template.enc", hash_file="template.hash"):
    """
    Calcule l'empreinte SHA-256 du fichier chiffré et la sauvegarde.
    """
    if not os.path.exists(file_path):
        print(f"Erreur : Le fichier {file_path} est introuvable. Relancez l'étape 2.")
        return

    # 1. Lire le fichier chiffré
    with open(file_path, "rb") as f:
        file_data = f.read()

    # 2. Calculer le hachage SHA-256
    sha256_hash = hashlib.sha256(file_data).hexdigest()

    # 3. Sauvegarder l'empreinte dans un fichier texte
    with open(hash_file, "w") as f:
        f.write(sha256_hash)

    print(f"SUCCÈS : Empreinte SHA-256 calculée : {sha256_hash}")
    print(f"L'empreinte a été sauvegardée dans : {hash_file}")

if __name__ == "__main__":
    calculate_and_save_hash()
