from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass(slots=True)
class Parcours:
    categorie: str
    etablissement: Optional[str] = None
    ville: Optional[str] = None
    dates: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "categorie": self.categorie,
            "etablissement": self.etablissement,
            "ville": self.ville,
            "dates": self.dates,
        }

@dataclass(slots=True)
class Profil:
    nom: str
    url: str
    id: Optional[str] = None
    lieu: Optional[str] = None
    type: Optional[str] = None
    parcours: List[Parcours] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nom": self.nom,
            "url": self.url,
            "id": self.id,
            "lieu": self.lieu,
            "type": self.type,
            "parcours": [p.to_dict() for p in self.parcours],
        }
