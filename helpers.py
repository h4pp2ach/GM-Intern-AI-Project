#!/usr/bin/env python
# helpers.py

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from prompt.config import PromptConfig
from typing import Optional

def none_if_blank_or_none_str(x: str) -> Optional[str]:
    if x is None:
        return None
    s = str(x).strip()
    if not s:
        return None
    if s.lower() == "none":
        return None
    return s


def build_suffix(
    provide_sources: bool,
    avoid_speculation: bool,
    allow_clarifying_questions: bool,
    three_variants: bool,
    lang_code: str,
) -> str:

    suffix_parts = []

    if lang_code == "ko":

        if provide_sources:
            suffix_parts.append("[NOTICE] 모든 정보에 대해 출처를 명시하고, 출처가 없으면 출처 없음을 명시하세요.")
        if avoid_speculation:
            suffix_parts.append("[NOTICE] 근거가 없는 추측성 답변을 금지하고, 확실하지 않은 항목은 모른다고 답변하세요.")
        if allow_clarifying_questions:
            suffix_parts.append("[NOTICE] 사용자의 질문이 모호하거나 핵심 정보가 부족하면, 필요에 따라 짧은 역질문으로 요구사항을 명확히 한 뒤 답변하세요.")
        if three_variants:
            suffix_parts.append("[NOTICE] 의미는 유지하고, 다양한 표현/톤으로 3개의 버전(V1, V2, V3)을 생성하세요.")

    else:  # English
        if provide_sources:
            suffix_parts.append("[NOTICE] Cite sources for all factual claims. If no source is available, explicitly state that no source is provided.")
        if avoid_speculation:
            suffix_parts.append("[NOTICE] Do not make speculative claims without evidence. If uncertain, explicitly state that you do not know.")
        if allow_clarifying_questions:
            suffix_parts.append("[NOTICE] If the request is ambiguous or lacks key information, ask a brief clarifying question before answering.")
        if three_variants:
            suffix_parts.append("[NOTICE] Generate three versions (V1, V2, V3) that preserve the original meaning while using different expressions and tones.")

    if not suffix_parts:
        return ""

    return "\n\n" + "\n".join(suffix_parts)


def build_user_input_section(user_input: str, lang_code: str) -> str:
    title = "사용자 입력" if lang_code == "ko" else "USER_INPUT"
    return f"\n\n[{title}]\n{user_input}"


def build_length_sentence(lang_label: str, length_mode: str) -> str:
    if length_mode == "default":
        return ""

    if lang_label == "Korean":
        if length_mode == "short":
            return "LENGTH: 핵심만 담아서 길지 않게 답하세요."
        if length_mode == "long":
            return "LENGTH: 최대한 빠지는 내용 없이 자세하게 조사해서 답하세요."
    else:
        if length_mode == "short":
            return "LENGTH: Keep it short and to the point, focusing only on the core information."
        if length_mode == "long":
            return "LENGTH: Be as thorough as possible and investigate carefully so nothing important is omitted."

    return ""

def build_role_block(
    lang_label: str,
    top_case: str,          # "1" | "2" | "3"  (top_case.startswith("1") 같은 걸 밖에서 정리해서 넣어도 됨)
    case_type: str,         # quick_info / translate / grammar_correction / rewrite_polish ...
    config: "PromptConfig",
) -> str:
    """
    Returns ROLE block text that fits your desired logic:
    - Sentence 1: always "<domain> 분야의 전문가입니다." (or inferred role)
    - Sentence 2:
        - top_case == "1": thinking_style + answer_tone
        - top_case in {"2","3"}: case-specific instruction (tone/style/scope/freedom)
    """

    # -------------------------
    # 1) ROLE 1문장(공통): "~분야의 전문가입니다."
    # -------------------------
    if lang_label == "Korean":
        if config.role_domain:
            s1 = f"당신은 {config.role_domain} 분야의 전문가입니다."
        else:
            s1 = "USER_INPUT을 바탕으로 가장 적절한 전문가 역할을 추론해 명시한 뒤, 해당 분야의 전문가로서 답변하세요."
    else:
        if config.role_domain:
            s1 = f"You are an expert in {config.role_domain}."
        else:
            s1 = "Infer and explicitly state the most appropriate expert role based on USER_INPUT, then respond as that expert."

    # -------------------------
    # 2) ROLE 2문장: top_case에 따라 분기
    # -------------------------
    s2 = ""

    if top_case == "1":
        if lang_label == "Korean":
            s2 = f"{config.thinking_style} 방식으로 사고하고, {config.answer_tone} 톤으로 응답하세요."
        else:
            s2 = f"Adopt a {config.thinking_style} reasoning style and respond in a {config.answer_tone} tone."

    else:
        if case_type == "translate":
            if lang_label == "Korean":
                tone_part = {
                    "neutral": "중립적인 톤으로 번역하세요",
                    "formal": "공식적인 톤으로 번역하세요",
                    "casual": "친근한 톤으로 번역하세요",
                }.get(config.translation_tone, "중립적인 톤으로 번역하세요")

                if config.translation_style == "literal":
                    style_part = "의역 없이 의미를 바꾸지 말고 정확하게 직역하세요"
                elif config.translation_style == "balanced":
                    style_part = "직역과 의역의 균형을 유지하되 의미는 정확히 보존하세요"
                else:  # natural
                    style_part = "의미를 유지하면서 최대한 자연스럽게 의역해 주세요"

                s2 = f"{tone_part}. {style_part}."
            else:
                tone_part = {
                    "neutral": "Translate in a neutral tone",
                    "formal": "Translate in a formal tone",
                    "casual": "Translate in a casual, friendly tone",
                }.get(config.translation_tone, "Translate in a neutral tone")

                if config.translation_style == "literal":
                    style_part = "be strictly literal and avoid paraphrasing"
                elif config.translation_style == "balanced":
                    style_part = "keep a balanced approach between literal translation and paraphrasing"
                else:
                    style_part = "prioritize naturalness and allow paraphrasing while preserving meaning"

                s2 = f"{tone_part}; {style_part}."

        elif case_type == "grammar_correction":
            if lang_label == "Korean":
                if config.grammar_scope == "grammar_vocab_only":
                    s2 = "문법과 어휘 오류만 최소 수정으로 고치고 문체/말투는 유지하세요."
                else:
                    tone_part = {
                        "keep": "톤은 원문을 최대한 유지하세요",
                        "formal": "톤을 공식적으로 맞추세요",
                        "casual": "톤을 친근하게 바꾸세요",
                        "professional": "톤을 더 전문적으로 다듬으세요",
                        "concise": "톤을 간결하게 정리하세요",
                    }.get(config.grammar_tone, "톤은 원문을 최대한 유지하세요")
                    s2 = f"문법/어휘 교정뿐 아니라 문장 흐름과 말투까지 자연스럽게 개선하세요. {tone_part}."
            else:
                if config.grammar_scope == "grammar_vocab_only":
                    s2 = "Make minimal edits focusing only on grammar and vocabulary, and keep the original style and tone."
                else:
                    tone_part = {
                        "keep": "keep the original tone",
                        "formal": "make the tone formal",
                        "casual": "make the tone casual",
                        "professional": "make the tone professional",
                        "concise": "make the tone concise",
                    }.get(config.grammar_tone, "keep the original tone")
                    s2 = f"Improve grammar and vocabulary and also enhance fluency and tone; {tone_part}."

        elif case_type == "rewrite_polish":
            if lang_label == "Korean":
                if config.polish_freedom == "low":
                    freedom_part = "원문의 표현과 구조를 최대한 유지하되 어색한 부분만 최소 수정으로 다듬으세요"
                elif config.polish_freedom == "high":
                    freedom_part = "의미를 유지하는 선에서 문장 구조 재작성까지 포함해 과감하게 다듬으세요"
                else:
                    freedom_part = "의미는 유지하되 전반적으로 자연스럽고 읽기 좋게 다듬으세요"

                tone_part = {
                    "keep": "톤은 원문을 유지하세요",
                    "professional": "톤을 더 전문적으로 다듬으세요",
                    "formal": "톤을 공식적으로 맞추세요",
                    "casual": "톤을 친근하게 바꾸세요",
                    "concise": "톤을 간결하게 정리하세요",
                }.get(config.polish_tone, "톤을 더 전문적으로 다듬으세요")

                s2 = f"{freedom_part}. {tone_part}."
            else:
                if config.polish_freedom == "low":
                    freedom_part = "make minimal edits and preserve the original wording/structure as much as possible"
                elif config.polish_freedom == "high":
                    freedom_part = "rewrite boldly (including restructuring) while preserving meaning"
                else:
                    freedom_part = "polish for clarity and naturalness while preserving meaning"

                tone_part = {
                    "keep": "keep the original tone",
                    "professional": "make the tone professional",
                    "formal": "make the tone formal",
                    "casual": "make the tone casual",
                    "concise": "make it concise",
                }.get(config.polish_tone, "make the tone professional")

                s2 = f"{freedom_part}; {tone_part}."

        else:
            s2 = ""

    return (s1 + (" " + s2 if s2 else "")).strip()