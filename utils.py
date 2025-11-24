import re
import uuid

def normalize_lemma(lemma: str) -> str:
    if not lemma.strip():
        raise ValueError("Lemma cannot be empty")
    lemma = lemma.strip().replace(' ', '_')
    if not re.match(r"^[a-zA-Z'_]+$", lemma):
        raise ValueError("Only letters, apostrophes, and underscores allowed")
    return lemma.lower()

def new_uuid() -> str:
    return str(uuid.uuid4())