import numpy as np
import cv2

def capture_biometric_template(user_id: str, use_webcam: bool = False) -> list:
    """
    Retourne un vecteur biométrique de 128 floats.
    - use_webcam=False : simulation déterministe (même vecteur pour même user_id)
    - use_webcam=True  : capture réelle via OpenCV (à activer si webcam disponible)
    """
    if use_webcam:
        return _capture_from_webcam()
    else:
        return _simulate_template(user_id)

def _simulate_template(user_id: str) -> list:
    """Simulation : seed basé sur user_id → résultat reproductible."""
    seed = abs(hash(user_id)) % (2**32)
    rng = np.random.default_rng(seed=seed)
    template = rng.random(128).tolist()
    print(f"[CAPTURE] Template simulé pour '{user_id}' — 128 dimensions")
    return template

def _capture_from_webcam() -> list:
    """Capture une frame webcam et retourne un vecteur aléatoire (placeholder)."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[CAPTURE] Webcam non disponible — passage en simulation")
        return _simulate_template("webcam_fallback")
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return _simulate_template("webcam_fallback")
    # Placeholder : en prod, remplacer par face_recognition.face_encodings()
    seed = int(frame.mean() * 1000) % (2**32)
    rng = np.random.default_rng(seed=seed)
    return rng.random(128).tolist()

if __name__ == "__main__":
    t = capture_biometric_template("alice")
    print(f"Template (5 premières valeurs) : {t[:5]}")
    print(f"Longueur : {len(t)}")