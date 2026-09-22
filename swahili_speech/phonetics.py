"""
Phonetic Grapheme-to-Phoneme (G2P) Rules for Swahili and Kikuyu
---------------------------------------------------------------
Author: James Nderi
License: MIT

Implements deterministic phonetic rules for:
1. Standard Kiswahili:
   - 5-vowel system: /a/, /e/, /i/, /o/, /u/
   - Digraphs and prenasalized consonants: ch, dh, gh, kh, ng', ny, sh, th, mb, nd, ng, nj
2. Kikuyu (Gĩkũyũ):
   - 7-vowel system: /a/, /e/ [ɛ], /i/, /o/ [ɔ], /u/, /ĩ/ [e], /ũ/ [o]
   - Orthographic digraphs: th [ð], ng [ŋ], ny [ɲ], mb [ᵐb], nd [ⁿd], nj [ⁿdʒ], ng' [ŋ]
"""

import re
from typing import List, Dict

# Standard Swahili G2P mapping table
SWAHILI_DIGRAPHS: Dict[str, str] = {
    "ng'": "ŋ",
    "ny": "ɲ",
    "ch": "tʃ",
    "dh": "ð",
    "gh": "ɣ",
    "kh": "x",
    "sh": "ʃ",
    "th": "θ",
    "mb": "ᵐb",
    "nd": "ⁿd",
    "ng": "ᵑɡ",
    "nj": "ⁿdʒ",
    "mv": "ᵐv",
    "nz": "ⁿz",
}

# Kikuyu G2P mapping table including the 7 phonemic vowels
KIKUYU_PHONEMES: Dict[str, str] = {
    "ĩ": "e",
    "ũ": "o",
    "th": "ð",
    "ng'": "ŋ",
    "ng": "ᵑɡ",
    "ny": "ɲ",
    "mb": "ᵐb",
    "nd": "ⁿd",
    "nj": "ⁿdʒ",
    "c": "ʃ",   # In Kikuyu orthography, 'c' is typically pronounced [ʃ] or [tʃ]
}

def normalize_text(text: str) -> str:
    """Cleans punctuation, normalizes whitespace, and converts to lowercase."""
    text = text.lower().strip()
    # Normalize common Unicode variants of Kikuyu tilde vowels
    text = text.replace("i\u0303", "ĩ").replace("u\u0303", "ũ")
    # Retain standard letters, tildes, apostrophe for ng', and spaces
    text = re.sub(r"[^a-zĩũ'\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text

def swahili_g2p(text: str) -> List[str]:
    """Converts normalized Swahili text into an IPA phoneme sequence."""
    norm = normalize_text(text)
    phonemes = []
    i = 0
    n = len(norm)
    
    while i < n:
        char = norm[i]
        
        # Check 3-character digraph (ng')
        if i + 3 <= n and norm[i:i+3] == "ng'":
            phonemes.append(SWAHILI_DIGRAPHS["ng'"])
            i += 3
            continue
            
        # Check 2-character digraphs
        if i + 2 <= n and norm[i:i+2] in SWAHILI_DIGRAPHS:
            phonemes.append(SWAHILI_DIGRAPHS[norm[i:i+2]])
            i += 2
            continue
            
        # Standard 1-to-1 character mapping
        if char == " ":
            phonemes.append(" ")
        elif char == "j":
            phonemes.append("ɟ")
        elif char == "y":
            phonemes.append("j")
        elif char == "w":
            phonemes.append("w")
        elif char in "aeioubdfghklmnprstvz":
            phonemes.append(char)
            
        i += 1
        
    return phonemes

def kikuyu_g2p(text: str) -> List[str]:
    """Converts normalized Kikuyu text into an IPA phoneme sequence."""
    norm = normalize_text(text)
    phonemes = []
    i = 0
    n = len(norm)
    
    while i < n:
        char = norm[i]
        
        # Check 3-character digraph (ng')
        if i + 3 <= n and norm[i:i+3] == "ng'":
            phonemes.append(KIKUYU_PHONEMES["ng'"])
            i += 3
            continue
            
        # Check 2-character digraphs
        if i + 2 <= n and norm[i:i+2] in KIKUYU_PHONEMES:
            phonemes.append(KIKUYU_PHONEMES[norm[i:i+2]])
            i += 2
            continue
            
        # Single character special substitutions
        if char in KIKUYU_PHONEMES:
            phonemes.append(KIKUYU_PHONEMES[char])
        elif char == "e":
            phonemes.append("ɛ")
        elif char == "o":
            phonemes.append("ɔ")
        elif char == " ":
            phonemes.append(" ")
        elif char in "aiubdfghklmnprstvw":
            phonemes.append(char)
            
        i += 1
        
    return phonemes

def text_to_phonemes(text: str, lang: str = "sw") -> List[str]:
    """Unified entry point for phonetic transcription."""
    if lang.lower() in ("ki", "kikuyu", "gikuyu"):
        return kikuyu_g2p(text)
    return swahili_g2p(text)

if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        
    # Self-test verification
    sw_sample = "Mwanafunzi anasoma kitabu cha Kiswahili"
    ki_sample = "Mũndũ mũrũme na mũndũ mũka nĩ mararĩma mũgũnda"
    
    print("Swahili Test:")
    print("Text:", sw_sample)
    print("IPA :", "".join(text_to_phonemes(sw_sample, "sw")))
    
    print("\nKikuyu Test:")
    print("Text:", ki_sample)
    print("IPA :", "".join(text_to_phonemes(ki_sample, "ki")))
