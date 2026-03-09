import re

def basic_cleanup(text: str) -> str:
    # normalize spaces
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def light_academic_cleanup(text: str) -> str:
    # remove super-chatty fillers (safe)
    fillers = [
        r"\bwell\b[, ]*",
        r"\bhonestly\b[, ]*",
        r"\byou know\b[, ]*",
        r"\bactually\b[, ]*",
        r"\blike\b[, ]*",
    ]
    out = text
    for pat in fillers:
        out = re.sub(pat, "", out, flags=re.IGNORECASE)
    out = re.sub(r"\s{2,}", " ", out).strip()
    return out

def sentence_count(text: str) -> int:
    parts = re.split(r"[.!?]+", text)
    parts = [p.strip() for p in parts if p.strip()]
    return len(parts)

def word_count(text: str) -> int:
    words = re.findall(r"\b\w+\b", text)
    return len(words)
