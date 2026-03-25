import numpy as np

def normalize_template(features: list) -> list:
    """Normalise un vecteur entre 0 et 1 (min-max scaling)."""
    arr = np.array(features, dtype=float)
    min_val, max_val = arr.min(), arr.max()
    if max_val - min_val < 1e-9:
        return [0.5] * len(features)
    normalized = (arr - min_val) / (max_val - min_val)
    return normalized.tolist()

def fragment_template(template: list) -> tuple:
    """
    Divise le template 128D en deux fragments de 64 valeurs.
    Retourne (fragment_a, fragment_b).
    fragment_a → stocké côté client
    fragment_b → envoyé au serveur
    """
    if len(template) != 128:
        raise ValueError(f"Template doit avoir 128 dimensions, reçu : {len(template)}")
    fragment_a = template[:64]
    fragment_b = template[64:]
    print(f"[TEMPLATE] Fragmentation : A={len(fragment_a)}D / B={len(fragment_b)}D")
    return fragment_a, fragment_b

def reconstruct_template(fragment_a: list, fragment_b: list) -> list:
    """Reconstruit le template complet à partir des deux fragments."""
    return fragment_a + fragment_b

def cosine_distance(v1: list, v2: list) -> float:
    """Calcule la distance cosinus entre deux vecteurs (0 = identiques)."""
    a, b = np.array(v1), np.array(v2)
    dot = np.dot(a, b)
    norms = np.linalg.norm(a) * np.linalg.norm(b)
    if norms < 1e-9:
        return 1.0
    return float(1.0 - dot / norms)

if __name__ == "__main__":
    from capture import capture_biometric_template
    raw = capture_biometric_template("bob")
    normalized = normalize_template(raw)
    fa, fb = fragment_template(normalized)
    reconstructed = reconstruct_template(fa, fb)
    dist = cosine_distance(normalized, reconstructed)
    print(f"Distance après reconstruction : {dist:.6f} (doit être ~0)")