class CopainsError(Exception):
    """Base pour toutes les erreurs."""
    pass

class CopainsNetworkError(CopainsError):
    """Erreur réseau (timeout, statut HTTP, connexion)."""
    pass

class CopainsParseError(CopainsError):
    """Erreur de parsing HTML."""
    pass
