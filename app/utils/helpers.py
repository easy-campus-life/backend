"""
Utilitaires génériques pour l'application
"""

from datetime import datetime
from typing import Any, Dict, Optional

def format_datetime(dt: datetime) -> str:
    """Formater une date/heure en string ISO"""
    return dt.isoformat() if dt else None

def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Récupérer une valeur de manière sécurisée d'un dictionnaire"""
    return data.get(key, default)

def validate_email_format(email: str) -> bool:
    """Validation basique du format email"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def truncate_text(text: str, max_length: int = 100) -> str:
    """Tronquer un texte à une longueur maximale"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..." 