import re
import unicodedata

def slugify(text: str) -> str:
    """Convertit un texte en slug ASCII sans accents, séparé par des underscores."""
    if text is None:
        return ''
    # Corrections pré-NFKD pour quelques caractères non décomposés (ex: turc ı)
    text = text.replace('ı', 'i').replace('İ', 'i')
    normalized = unicodedata.normalize('NFKD', text)
    ascii_text = normalized.encode('ascii', 'ignore').decode('ascii')
    ascii_text = ascii_text.lower()
    ascii_text = re.sub(r'[^a-z0-9]+', '_', ascii_text)
    return ascii_text.strip('_')
