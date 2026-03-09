from typing import Dict

def readability_scores(text: str) -> Dict[str, float]:
    try:
        import textstat
        return {
            "flesch_reading_ease": float(textstat.flesch_reading_ease(text)),
            "flesch_kincaid_grade": float(textstat.flesch_kincaid_grade(text)),
        }
    except Exception:
        return {
            "flesch_reading_ease": 0.0,
            "flesch_kincaid_grade": 0.0,
        }
