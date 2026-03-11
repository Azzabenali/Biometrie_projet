import face_recognition
import numpy as np
import json
import time
import os

def create_biometric_template(image_path="captured_face.jpg", user_id="user_001"):
    """
    Étapes 3 à 6 : Extraction, normalisation, structuration et sauvegarde JSON.
    """
    if not os.path.exists(image_path):
        print(f"Erreur : L'image {image_path} n'existe pas.")
        return None

    # Chargement de l'image capturée
    image = face_recognition.load_image_file(image_path)

    # Étape 2 : Détection du visage
    face_locations = face_recognition.face_locations(image)
    
    if not face_locations:
        print("Erreur : Aucun visage détecté sur l'image.")
        return None

    # Étape 3 : Extraction du vecteur biométrique (128 valeurs)
    # On prend le premier visage détecté
    encodings = face_recognition.face_encodings(image, face_locations)
    if not encodings:
        print("Erreur : Impossible d'extraire les caractéristiques du visage.")
        return None
    
    encoding = encodings[0]

    # Étape 4 : Normalisation (0 -> 1) avec numpy
    # Les vecteurs face_recognition sont déjà normalisés (L2 norm), 
    # mais pour suivre la consigne d'une transformation vers [0, 1] :
    min_val = np.min(encoding)
    max_val = np.max(encoding)
    normalized_encoding = (encoding - min_val) / (max_val - min_val)

    # Étape 5 : Structure du template
    template = {
        "user_id": user_id,
        "features": normalized_encoding.tolist(),  # Conversion numpy -> list pour JSON
        "timestamp": time.time()
    }

    # Étape 6 : Sauvegarde en JSON
    output_file = "template.json"
    with open(output_file, 'w') as f:
        json.dump(template, f, indent=4)
    
    print(f"Template biométrique sauvegardé avec succès dans : {output_file}")
    return template

if __name__ == "__main__":
    create_biometric_template()