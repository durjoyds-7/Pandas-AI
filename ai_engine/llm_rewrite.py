import requests
import re

OLLAMA_URL = "http://localhost:11434/api/generate"

SYSTEM_STYLE = """You are Pandas-AI, a thesis/research writing assistant.

NON-NEGOTIABLE RULES:
1) Preserve the original meaning exactly. 
2) Keep technical terms, symbols, numbers,units, hyperparameters, and method names unchanged unless grammar requires a minor adjustment.
3) Do NOT invent research framing (e.g., "recent studies indicate") unless present in input.
4) Output ONLY the rewritten text. 
5) Keep the same language as the input.

STYLE GOAL:
- Product polished academic prose suitable for thesis, dissertation, or research writing. 
- Improve clarity, coherence, sentence flow, and formal tone.
- Avoid casule phrasing, vangue wording, and repetitive structures.
- Prefer concise, precise, and logically connected sentences.
- Keep it concise; do not inflate.
- Do not make the text unnecessarily longer.
"""

def _instruction(mode: str) -> str:
    mode = (mode or "thesis").lower().strip()
    if mode == "thesis":
        return "Rewrite as thesis-ready academic prose. Improve clarity and flow. Avoid formulaic openings."
    if mode == "academic":
        return "Rewrite in formal academic tone. Avoid contractions. Keep it concise and objective."
    if mode == "human":
        return "Rewrite to sound natural and human-written while staying academically appropriate."
    if mode == "simplify":
        return "Rewrite using simpler words and shorter sentences while keeping meaning and technical terms."
    if mode == "expand":
        return "Rewrite with slightly richer explanation while keeping meaning. Do NOT add new facts."
    if mode == "formal":
        return "Rewrite in a very formal, polished tone. Keep it concise."
    return "Rewrite in a balanced thesis-friendly tone: clear, concise, readable, and natural."

def _strength_params(strength: str):
    strength = (strength or "medium").lower().strip()
    if strength == "low":
        return {"temperature": 0.18, "top_p": 0.82, "repeat_penalty": 1.10}
    if strength == "strong":
        return {"temperature": 0.32, "top_p": 0.90, "repeat_penalty": 1.12}
    return {"temperature": 0.24, "top_p": 0.86, "repeat_penalty": 1.11}

def _split_into_chunks(text: str, max_chars: int = 1500):
    text = (text or "").strip()
    if not text:
        return []
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, buf = [], ""
    for p in paras:
        if len(buf) + len(p) + 2 <= max_chars:
            buf = (buf + "\n\n" + p).strip()
        else:
            if buf:
                chunks.append(buf)
            if len(p) <= max_chars:
                chunks.append(p)
            else:
                for i in range(0, len(p), max_chars):
                    chunks.append(p[i:i + max_chars])
            buf = ""
    if buf:
        chunks.append(buf)
    return chunks

def _postprocess(text: str) -> str:
    if not text:
        return ""
    t = text.strip()
    # remove model boilerplate lines (safe cleanup)
    prefaces = [
        r"^Here(?:'s| is) the rewritten text.*?:\s*",
        r"^Rewritten text.*?:\s*",
        r"^In a (?:balanced|academic|formal|human|thesis)[\w\s-]* tone.*?:\s*",
    ]
    for pat in prefaces:
        t = re.sub(pat, "", t, flags=re.IGNORECASE | re.DOTALL).strip()
    t = re.sub(r"\n{3,}", "\n\n", t)
    t = re.sub(r"[ \t]{2,}", " ", t)
    return t.strip()

def _call_ollama(chunk: str, mode: str, strength: str, model: str) -> str:
    instr = _instruction(mode)
    opts = _strength_params(strength)

    writing_guidance = (
        "WRITING GUIDANCE:\n"
        "- Keep technical values unchanged.\n"
        "- Vary sentence length naturally.\n"
        "- Avoid repeating the same opener across sentences.\n"
        "- Keep the same level of detail; do not embellish.\n"
        "- Do not add citations or literature claims.\n"
    )

    prompt = f"""{SYSTEM_STYLE}

MODE: {mode}
STRENGTH: {strength}
INSTRUCTION: {instr}

{writing_guidance}

TEXT:
{chunk}

OUTPUT (rewritten text only):
"""

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            **opts,
            "num_predict": 220,
            "num_ctx": 1024
        }
    }

    r = requests.post(OLLAMA_URL, json=payload, timeout=600)
    r.raise_for_status()
    return _postprocess((r.json().get("response") or "").strip())

def llm_rewrite(text: str, mode: str = "thesis", strength: str = "medium", model: str = "llama3:latest") -> str:
    chunks = _split_into_chunks(text, max_chars=900)
    if not chunks:
        return ""
    outputs = []
    for ch in chunks:
        try:
            outputs.append(_call_ollama(ch, mode, strength, model))
        except requests.exceptions.ConnectionError:
            return "ERROR: Ollama server is not running. Start Ollama and try again."
        except requests.exceptions.Timeout:
            return "ERROR: Ollama timed out. Try smaller text or set Strength=low."
        except Exception as e:
            return f"ERROR: {e}"
    return "\n\n".join([o for o in outputs if o]).strip()
