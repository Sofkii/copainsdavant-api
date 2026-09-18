from .client import CopainsClient
from .models import Profil, Parcours
from .exceptions import CopainsError, CopainsNetworkError, CopainsParseError

__version__ = "1.0.0"
__all__ = [
    "CopainsClient",
    "Profil",
    "Parcours",
    "CopainsError",
    "CopainsNetworkError",
    "CopainsParseError",
]
