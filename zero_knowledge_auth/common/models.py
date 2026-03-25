from dataclasses import dataclass
from typing import List, Optional

@dataclass
class BiometricTemplate:
    user_id: str
    features: List[float]   # 128 floats normalisés [0, 1]
    timestamp: int
    version: str = "1.0"

    def validate(self) -> bool:
        return len(self.features) == 128 and all(0.0 <= f <= 1.0 for f in self.features)

@dataclass
class FragmentPair:
    fragment_a: List[float]   # 64 valeurs — reste côté client
    fragment_b: List[float]   # 64 valeurs — envoyées au serveur

@dataclass
class EnrollRequest:
    user_id: str
    fragment_b: List[float]

@dataclass
class AuthRequest:
    user_id: str
    auth_result: bool
    score: Optional[float] = None