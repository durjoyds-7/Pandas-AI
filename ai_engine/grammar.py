from dataclasses import dataclass
from typing import List, Optional

@dataclass
class GrammarIssue:
    message: str
    offset: int
    error_length: int
    rule_id: str

_tool = None
_tool_error: Optional[str] = None

def _init_tool():
    global _tool, _tool_error
    if _tool is not None or _tool_error is not None:
        return
    try:
        import language_tool_python
        _tool = language_tool_python.LanguageTool("en-US")
    except Exception as e:
        _tool_error = str(e)

def check_grammar(text: str) -> List[GrammarIssue]:
    _init_tool()
    if _tool is None:
        return []

    matches = _tool.check(text)
    issues: List[GrammarIssue] = []
    for m in matches[:30]:  # cap
        issues.append(
            GrammarIssue(
                message=getattr(m, "message", ""),
                offset=getattr(m, "offset", 0),
                error_length=getattr(m, "errorLength", 0),
                rule_id=getattr(getattr(m, "rule", None), "id", "") if getattr(m, "rule", None) else ""
            )
        )
    return issues

def tool_status() -> str:
    _init_tool()
    if _tool is not None:
        return "ok"
    return f"disabled ({_tool_error})" if _tool_error else "disabled"
