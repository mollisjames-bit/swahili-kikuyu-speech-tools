"""
Swahili and Kikuyu Speech Tools Package
"""
from .phonetics import text_to_phonemes, normalize_text, swahili_g2p, kikuyu_g2p

__version__ = "0.1.0"
__all__ = ["text_to_phonemes", "normalize_text", "swahili_g2p", "kikuyu_g2p"]
