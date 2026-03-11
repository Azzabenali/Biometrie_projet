import cv2
import os

def capture_image(output_path="captured_face.jpg"):
    """
    Étape 1 & 2 : Capture webcam et détection de visage simple.
    """
    # Initialisation de la webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Erreur : Impossible d'accéder à la webcam.")
        return False

    print("Appuyez sur 'Espace' pour capturer l'image ou 'q' pour quitter.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erreur lors de la lecture du flux vidéo.")
            break

        # Affichage du flux en direct
        cv2.imshow("Capture Biométrique - Appuyez sur Espace", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):  # Touche Espace pour capturer
            cv2.imwrite(output_path, frame)
            print(f"Image sauvegardée sous : {output_path}")
            break
        elif key == ord('q'): # Touche q pour quitter sans capturer
            print("Capture annulée.")
            break

    # Libération des ressources
    cap.release()
    cv2.destroyAllWindows()
    return os.path.exists(output_path)

if __name__ == "__main__":
    capture_image()