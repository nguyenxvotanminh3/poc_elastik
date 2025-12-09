# services/deduplicator.py
"""
STRICT Deduplication Module
Only allows 100% exact matches - any character difference = duplicate removal
No normalization, no similarity checking - pure exact string comparison
"""
from typing import Set, List, Dict, Any


def normalize_text(text: str) -> str:
    """
    DEPRECATED: No longer used in strict mode.
    Returns text as-is without any normalization.
    """
    return text


def get_text_fingerprint(text: str, first_n_words: int = 5) -> str:
    """
    DEPRECATED: No longer used in strict mode.
    Returns text as-is.
    """
    return text


def calculate_similarity(text1: str, text2: str) -> float:
    """
    STRICT MODE: Only returns 1.0 (100%) if texts are EXACTLY identical.
    Any difference in character, case, space, punctuation = 0.0
    """
    return 1.0 if text1 == text2 else 0.0


def is_duplicate(
    text: str, 
    seen_texts: Set[str],
    similarity_threshold: float = 1.0,  # STRICT: Always 100%
    fingerprint_match: bool = False  # STRICT: Disabled
) -> bool:
    """
    STRICT MODE: Check if text is 100% exact match with any seen text.
    
    Any character difference (case, space, punctuation) = NOT a duplicate.
    Only EXACTLY identical strings are considered duplicates.
    
    Args:
        text: Text to check
        seen_texts: Set of previously seen texts
        similarity_threshold: IGNORED (always 100%)
        fingerprint_match: IGNORED (disabled)
        
    Returns:
        True only if exact match found
    """
    if not text or not seen_texts:
        return False
    
    # STRICT: Only exact string match
    return text in seen_texts


def deduplicate_sentences(
    sentences: List[Dict[str, Any]],
    existing_texts: Set[str] = None,
    similarity_threshold: float = 1.0,  # STRICT: Always 100%
    use_fingerprint: bool = False  # STRICT: Disabled
) -> List[Dict[str, Any]]:
    """
    STRICT MODE: Remove sentences that are not 100% exactly identical.
    
    Even 1 character difference (case, space, punctuation) = keep as unique.
    Only EXACTLY identical strings are removed.
    
    Args:
        sentences: List of sentence dicts with 'text' field
        existing_texts: Set of texts already seen (to exclude)
        similarity_threshold: IGNORED (always 100%)
        use_fingerprint: IGNORED (disabled)
        
    Returns:
        List with only 100% exact duplicates removed
    """
    if not sentences:
        return []
    
    seen = set(existing_texts) if existing_texts else set()
    unique = []
    
    for sent in sentences:
        text = sent.get("text", "")
        if not text:
            continue
            
        # STRICT: Only exact string match checking
        if text not in seen:
            seen.add(text)
            unique.append(sent)
    
    return unique


def get_unique_key(text: str) -> str:
    """
    STRICT MODE: Returns text as-is (no normalization).
    Each character matters - even case and spaces.
    """
    return text
