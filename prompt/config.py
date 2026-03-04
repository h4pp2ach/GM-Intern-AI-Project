from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class PromptConfig:

    top_case_id: str = "1"

    role_domain: Optional[str] = None
    thinking_style: str = ""
    answer_tone: str = ""
    goal: str = ""

    audience: Optional[str] = None
    time_range: Optional[str] = None
    depth: Optional[str] = None
    length_limit: Optional[int] = None

    provide_sources: bool = True
    avoid_speculation: bool = False
    output_structure: Optional[str] = None

    extra_instructions: List[str] = field(default_factory=list)
    prompt_language: str = "ko"
    length_mode: str = "default"
    user_input: str = ""

    # ===== Case-specific options =====
    # translate
    translation_style: str = "natural"  # literal | balanced | natural
    translation_tone: str = "neutral"   # neutral | formal | casual

    # grammar_correction
    grammar_scope: str = "grammar_vocab_only"  # grammar_vocab_only | include_tone
    grammar_tone: str = "keep"                 # keep | formal | casual | professional | concise

    # rewrite_polish
    polish_freedom: str = "medium"             # low | medium | high
    polish_tone: str = "professional"          # keep | professional | formal | casual | concise
