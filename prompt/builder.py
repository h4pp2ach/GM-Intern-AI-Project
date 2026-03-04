#!/usr/bin/env python
# prompt_builder.py

import json
from pathlib import Path
from .config import PromptConfig
from typing import List, Dict

from helpers import build_role_block, build_length_sentence

TEMPLATE_PATH = Path(__file__).parent / "case_templates.json"

with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    case_templates = json.load(f)


def generate_prompt(config: PromptConfig, case_type: str) -> List[Dict[str, str]]:

    if case_type not in case_templates:
        raise ValueError(f"Unknown case_type: {case_type}")

    template = case_templates[case_type]
    Components = ", ".join(template["sections"])

    lang_label = "Korean" if config.prompt_language == "ko" else "English"

    role_description = build_role_block(
        lang_label=lang_label,
        top_case=config.top_case_id,
        case_type=case_type,
        config=config,
    )

    length_sentence = build_length_sentence(lang_label, config.length_mode)

    system_content = (
        "You are a senior prompt engineer.\n"
        "You MUST generate a downstream prompt (NOT an answer).\n"
        f"Output language: {lang_label}.\n"

        "CRITICAL:\n"
        "- Do NOT answer USER_INPUT.\n"
        "- Output ONLY the downstream prompt text. No preface, no explanation, no examples.\n"
        "- Do NOT include analysis, reasoning, or <think>.\n\n"
        
        "OUTPUT TEMPLATE (must follow exactly):\n"
        "- Output must be a SINGLE paragraph (no headings, no bullet points, no numbered lists)\n"
        "- The paragraph must contain exactly these components in this order: ROLE → TASK → (optional SCOPE) → EVIDENCE POLICY → OUTPUT COMPONENTS.\n"
        
        "[ROLE]\n"
        f"role description: {role_description}\n"
        "- 1 sentences: domain expertise + thinking style + response tone.\n"
        "- If no role is explicitly specified, infer and assign an appropriate expert role based on USER_INPUT.\n\n"
        
        "[TASK]\n"
        "- 1 to 2 sentences: goal + target audience[optional].\n\n"
        
        "[SCOPE]\n"
        "- OPTIONAL: If time_range or depth is provided, include exactly 1 sentence. If not provided, OMIT this section.\n\n"
        
        "[OUTPUT COMPONENTS]\n"
        "- Exactly 1 sentence starting with 'COMPONENTS:' require the answer to include at least these keywords (not a strict format):"
        
        f"{Components}.\n\n"
        "SELF-CHECK (silent):\n"
        "- Ensure ROLE/TASK/SCOPE/OUTPUT COMPONENTS prefixes exist.\n"
        "- Remove semantically redundant content.\n"
        "- Ensure the final sentence is rewritten to sound natural and fluent\n"
        "- If anything violates the template, revise internally and output only the final prompt.\n"
    )

    # -------------------------
    # 2) User 메시지 구성
    # -------------------------
    user_lines: List[str] = []

    # Task / Audience
    user_lines.append(f"Goal: {config.goal}. Audience: {config.audience}.")

    # Scope
    if config.time_range:
        user_lines.append(f"Time range: {config.time_range}.")
    if config.depth:
        user_lines.append(f"Analysis depth: {config.depth}.")

    if config.length_mode != "default":
        user_lines.append(
            "Length requirement:\n"
            f"- In the downstream prompt, include this exact sentence: {length_sentence}"
        )

    # Case description
    user_lines.append(f"USER_INPUT:\n{config.user_input}")
    user_lines.append(template["description"])

    user_lines.append(
        "Output format constraint:\n"
        "- The final output must be ONE concise instruction prompt.\n"
        "- Maximum 4 sentences.\n"
        "- Do NOT generate the answer to USER_INPUT.\n"
        "- Do NOT include explanations, examples, or commentary.\n"
    )

    if config.output_structure:
        user_lines.append(
            "In the downstream prompt, enforce this output structure:\n"
            f"{config.output_structure}"
        )

    if config.length_limit:
        user_lines.append(
            f"In the downstream prompt, enforce a length limit of ~{config.length_limit} words."
        )

    # Extra instructions
    for instruction in config.extra_instructions:
        user_lines.append(instruction)

    user_content = "\n".join(user_lines)

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content},
    ]