import re
from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class Suggestion:
    type: str          # "tighten" | "redundancy" | "clarity"
    message: str
    before: str = ""
    after: str = ""

# ---- Sentence tightening rules (meaning-preserving) ----
_TIGHTEN_RULES: List[Tuple[str, str]] = [
    (r"\bdue to the fact that\b", "because"),
    (r"\bin order to\b", "to"),
    (r"\bat this point in time\b", "now"),
    (r"\ba large number of\b", "many"),
    (r"\ba small number of\b", "few"),
    (r"\bhas the ability to\b", "can"),
    (r"\bis able to\b", "can"),
    (r"\bin the event that\b", "if"),
    (r"\bwith regard to\b", "regarding"),
    (r"\bwith respect to\b", "regarding"),
    (r"\bfor the purpose of\b", "for"),
    (r"\bit is important to note that\b", "notably,"),
    (r"\bit should be noted that\b", "notably,"),
    (r"\bthere is a need to\b", "we need to"),
]

_HEDGE_RULES: List[Tuple[str, str]] = [
    (r"\bvery\b", ""),
    (r"\breally\b", ""),
    (r"\bquite\b", ""),
]

_FILLERS = [
    r"\bbasically\b",
    r"\bessentially\b",
    r"\bin general\b",
    r"\bas a matter of fact\b",
]

def _normalize_space(text: str) -> str:
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def tighten_text(text: str) -> Tuple[str, List[Suggestion]]:
    """
    Conservative tightening. Returns (tightened_text, suggestions).
    """
    suggestions: List[Suggestion] = []
    out = text

    for pat, rep in _TIGHTEN_RULES:
        if re.search(pat, out, flags=re.IGNORECASE):
            before = re.findall(pat, out, flags=re.IGNORECASE)[0]
            out = re.sub(pat, rep, out, flags=re.IGNORECASE)
            suggestions.append(Suggestion(
                type="tighten",
                message="Replace wordy phrase with a concise equivalent.",
                before=before,
                after=rep
            ))

    for fp in _FILLERS:
        if re.search(fp, out, flags=re.IGNORECASE):
            before = re.findall(fp, out, flags=re.IGNORECASE)[0]
            out = re.sub(fp, "", out, flags=re.IGNORECASE)
            suggestions.append(Suggestion(
                type="tighten",
                message="Remove filler word/phrase to improve concision.",
                before=before,
                after=""
            ))

    for pat, rep in _HEDGE_RULES:
        if re.search(pat, out, flags=re.IGNORECASE):
            before = re.findall(pat, out, flags=re.IGNORECASE)[0]
            out = re.sub(pat, rep, out, flags=re.IGNORECASE)
            suggestions.append(Suggestion(
                type="tighten",
                message="Remove unnecessary intensifier for a more academic tone.",
                before=before,
                after=rep
            ))

    out = _normalize_space(out)
    return out, suggestions

def redundancy_suggestions(text: str) -> List[Suggestion]:
    """
    Heuristics for redundancy: duplicate sentences, repeated openings, repeated phrases.
    """
    suggestions: List[Suggestion] = []
    t = _normalize_space(text)

    sentences = re.split(r"(?<=[.!?])\s+", t)
    sentences = [s.strip() for s in sentences if s.strip()]

    # Duplicate sentences
    seen = set()
    for s in sentences:
        key = re.sub(r"\W+", "", s.lower())
        if key in seen and len(s.split()) > 6:
            suggestions.append(Suggestion(
                type="redundancy",
                message="A sentence appears repeated. Consider removing or merging it.",
                before=s,
                after=""
            ))
        seen.add(key)

    # Repeated sentence openings (first 4 words)
    openings: Dict[str, int] = {}
    for s in sentences:
        words = re.findall(r"\b\w+\b", s.lower())
        opener = " ".join(words[:4])
        if len(opener.split()) >= 3:
            openings[opener] = openings.get(opener, 0) + 1
    for opener, cnt in openings.items():
        if cnt >= 3:
            suggestions.append(Suggestion(
                type="redundancy",
                message=f"Many sentences start similarly ('{opener}...'). Vary openings to improve flow.",
            ))

    # Repeated phrases (simple n-gram)
    words = re.findall(r"\b\w+\b", t.lower())
    for n in (3, 4):
        grams = {}
        for i in range(len(words) - n + 1):
            g = " ".join(words[i:i+n])
            if len(g) < 24:
                grams[g] = grams.get(g, 0) + 1
        frequent = sorted([(g,c) for g,c in grams.items() if c >= 4], key=lambda x: -x[1])[:5]
        for g, c in frequent:
            suggestions.append(Suggestion(
                type="redundancy",
                message=f"Phrase repeated {c} times ('{g}'). Consider rephrasing or removing repetition."
            ))

    return suggestions[:10]

def clarity_report(text: str) -> Dict:
    """
    A practical (non-scientific) clarity score dashboard for academic writing.
    """
    t = _normalize_space(text)
    if not t:
        return {"score": 0, "avg_sentence_length": 0.0, "long_sentence_count": 0, "passive_hits": 0, "tips": ["Provide some text to analyze."]}

    sentences = re.split(r"(?<=[.!?])\s+", t)
    sentences = [s.strip() for s in sentences if s.strip()]

    word_list = re.findall(r"\b\w+\b", t)
    wc = len(word_list)
    sc = max(1, len(sentences))
    avg_sent_len = wc / sc

    passive_hits = len(re.findall(r"\b(was|were|is|are|been|be)\b\s+\w+ed\b", t, flags=re.IGNORECASE))
    long_sent = sum(1 for s in sentences if len(re.findall(r"\b\w+\b", s)) >= 28)

    score = 100
    tips = []

    if avg_sent_len > 24:
        score -= 15
        tips.append("Average sentence length is high. Split a few long sentences for readability.")
    if long_sent >= 2:
        score -= 10
        tips.append("Multiple very long sentences detected. Consider splitting or simplifying them.")
    if passive_hits >= 3:
        score -= 8
        tips.append("Frequent passive constructions detected. Use active voice where appropriate for clarity.")

    long_words = sum(1 for w in word_list if len(w) >= 12)
    if wc > 0 and (long_words / wc) > 0.18:
        score -= 6
        tips.append("High density of long words. Consider simpler wording for a few sentences if appropriate.")

    score = max(0, min(100, score))
    if score >= 85 and not tips:
        tips.append("Clarity looks strong. Consider tightening a few phrases for extra polish.")

    return {
        "score": score,
        "avg_sentence_length": round(avg_sent_len, 1),
        "long_sentence_count": long_sent,
        "passive_hits": passive_hits,
        "tips": tips[:6]
    }
