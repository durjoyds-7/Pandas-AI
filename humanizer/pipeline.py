from .rules import basic_cleanup, light_academic_cleanup

def preprocess_text(text: str) -> str:
    text = basic_cleanup(text)
    text = light_academic_cleanup(text)
    return text
