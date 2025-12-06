"""
Utility Functions
Helpers pour mixer detection, etc.
"""
from typing import Dict, List
from config import Config


def check_mixer_flags(addresses: List[str]) -> List[Dict]:
    """
    Vérifie si des adresses sont liées à des mixers connus
    """
    flags = []
    known_mixers_lower = {m.lower() for m in Config.KNOWN_MIXERS}
    
    for address in addresses:
        is_mixer = address.lower() in known_mixers_lower
        
        # Vérifier aussi les connexions directes (si on a les données)
        # Pour MVP, on vérifie seulement les adresses exactes
        
        flags.append({
            "address": address,
            "is_mixer": is_mixer,
            "mixer_type": "Tornado Cash" if is_mixer else None
        })
    
    return flags


def format_address(address: str) -> str:
    """Formate une adresse pour affichage"""
    if len(address) > 10:
        return f"{address[:6]}...{address[-4:]}"
    return address

