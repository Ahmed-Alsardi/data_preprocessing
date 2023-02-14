from maha.cleaners.functions import normalize, keep


def clean_text(text: str) -> str:
    """
    Clean text using maha library.
    Normalize `alef` and keep only arabic letters.
    """
    text = normalize(text, alef=True)
    text = keep(text, arabic_letters=True)
    return text
