#!/usr/bin/env python
# app.py
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Iterator

from prompt.config import PromptConfig
from prompt.builder import generate_prompt
from helpers import none_if_blank_or_none_str, build_suffix, build_user_input_section

import requests
import streamlit as st


# =============================================================================
# Config load
# =============================================================================
# def load_config(config_path: str = "config.json") -> dict:
#     with open(config_path, "r", encoding="utf-8") as f:
#         return json.load(f)
BEARER_TOKEN = st.secrets["BEARER_TOKEN"]
ASMS_HEADER = st.secrets["ASMS_HEADER"]
MODEL_URL = st.secrets["MODEL_URL"]
MODEL_NAME = st.secrets["MODEL_NAME"]

# =============================================================================
# LLM call (non-stream)
# =============================================================================
def call_llm(
    messages: List[Dict[str, Any]],
    model_url: str,
    model_name: str,
    bearer_token: str,
    asms_header: Optional[str],
    max_tokens: int = 2048,
    temperature: float = 0.1,
    top_p: float = 0.9,
) -> str:
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }
    if asms_header:
        headers["asms"] = asms_header

    payload: Dict[str, Any] = {
        "model": model_name,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
    }

    try:
        resp = requests.post(model_url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as exc:
        return f"Error calling model API: {exc}"


# =============================================================================
# LLM call (streaming)
# =============================================================================
def call_llm_stream(
    messages: List[Dict[str, Any]],
    model_url: str,
    model_name: str,
    bearer_token: str,
    asms_header: Optional[str],
    max_tokens: int = 2048,
    temperature: float = 0.1,
    top_p: float = 0.9,
) -> Iterator[str]:

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }
    if asms_header:
        headers["asms"] = asms_header

    payload: Dict[str, Any] = {
        "model": model_name,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "stream": True,
    }

    with requests.post(model_url, headers=headers, json=payload, stream=True, timeout=120) as resp:
        resp.raise_for_status()
        resp.encoding = "utf-8"

        for raw in resp.iter_lines(decode_unicode=False):
            if not raw:
                continue

            line = raw.decode("utf-8", errors="replace").strip()

            if "data:" in line:
                line = line.split("data:", 1)[1].strip()

            if line == "[DONE]":
                break
            if not line or line.startswith(":"):
                continue

            try:
                data = json.loads(line)
            except Exception:
                continue

            choices = data.get("choices", [])
            if not choices:
                continue

            c0 = choices[0]
            delta = c0.get("delta", {})
            if isinstance(delta, dict) and delta.get("content"):
                yield delta["content"]
                continue

            msg = c0.get("message", {})
            if isinstance(msg, dict) and msg.get("content"):
                yield msg["content"]
                continue

            if c0.get("text"):
                yield c0["text"]
                continue

# =============================================================================
# Streamlit main
# =============================================================================
def main():
    st.set_page_config(page_title="Prompt Generator Demo", layout="wide")
    st.title("🧩 Prompt Generator Demo")

    st.markdown(
        """
        <style>
        /* ===== Radio -> Tab-like UI ===== */
        div[role="radiogroup"] {
            gap: 8px;
        }
        div[role="radiogroup"] > label {
            border: 1px solid rgba(49,51,63,.2);
            border-radius: 10px;
            padding: 8px 12px;
            margin-right: 6px;
            cursor: pointer;
        }
        div[role="radiogroup"] > label:has(input:checked) {
            border: 1px solid rgba(49,51,63,.6);
            background: rgba(49,51,63,.06);
            font-weight: 600;
        }

        /* ===== st.code: wrap visually (keep copy button) ===== */
        .stCodeBlock pre,
        .stCodeBlock pre code,
        div[data-testid="stCodeBlock"] pre,
        div[data-testid="stCodeBlock"] pre code {
            white-space: pre-wrap !important;
            word-break: break-word !important;
            overflow-wrap: anywhere !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    FLOATING_BUTTON_URL = "https://generalmotors.glean.com/chat"

    st.markdown(
        f"""
        <style>
        .floating-link-btn {{
            position: fixed;
            right: 22px;
            bottom: 22px;
            z-index: 9999;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 12px 16px;
            border-radius: 999px;
            border: 1px solid rgba(49,51,63,.2);
            background: rgba(255,255,255,.92);
            box-shadow: 0 8px 24px rgba(0,0,0,.12);
            font-weight: 600;
            text-decoration: none;
            color: inherit;
            backdrop-filter: blur(8px);
        }}
        .floating-link-btn:hover {{
            border-color: rgba(49,51,63,.5);
            box-shadow: 0 10px 28px rgba(0,0,0,.18);
        }}
        .floating-link-btn:active {{
            transform: translateY(1px);
        }}
        </style>

        <a class="floating-link-btn" href="{FLOATING_BUTTON_URL}" target="_blank" rel="noopener noreferrer">
        🔗 바로 질문하러 갈까요?
        </a>
        """,
        unsafe_allow_html=True,
    )

    # cfg = load_config("config.json")
    # MODEL_URL = cfg.get("MODEL_URL", "")
    # MODEL_NAME = cfg.get("MODEL_NAME", "")
    # BEARER_TOKEN = cfg.get("BEARER_TOKEN", "")
    # ASMS_HEADER = cfg.get("ASMS_HEADER", "")

    # -------------------------
    # 1) Top-level case 선택
    # -------------------------
    st.markdown("#### Case 선택")
    top_case = st.selectbox(
        label="",
        options=[
            "1. 🔎 정보 탐색 및 정리",
            "2. ✍️ 번역 및 문법 교정",
            "3. ✨ 문장(표현) 다듬기",
        ],
        index=0,
        label_visibility="collapsed",
        key="top_case",
    )
    top_case_id = top_case.split(".", 1)[0].strip()

    # top_case 변경 시 하위 위젯 상태 초기화(옵션 불일치 에러 방지)
    if "prev_top_case" not in st.session_state:
        st.session_state.prev_top_case = top_case
    if st.session_state.prev_top_case != top_case:
        for k in [
            "subcase_info",
            "subcase_translate_grammar",
            "subcase_polish",
            "translation_style_ui",
            "translation_tone_ui",
            "grammar_scope_ui",
            "grammar_tone_ui",
            "polish_freedom_ui",
            "polish_tone_ui",
        ]:
            if k in st.session_state:
                del st.session_state[k]
        st.session_state.prev_top_case = top_case

    # -------------------------
    # 2) 세부 Case 선택
    # -------------------------
    st.markdown("##### 세부 Case")

    if top_case_id == "1":
        label_map = {
            "빠른 정보 탐색": "quick_info",
            "비교 탐색": "comparison",
            "시장/트렌드 분석": "market_trend",
            "의사 결정": "decision_brief",
        }
        picked = st.radio(
            "subcase_info_label",
            options=list(label_map.keys()),
            horizontal=True,
            label_visibility="collapsed",
            key="subcase_info",
        )
        selected_sub = label_map[picked]

    elif top_case_id == "2":
        label_map = {
            "번역": "translate",
            "문법 교정": "grammar_correction",
        }
        picked = st.radio(
            "subcase_translate_grammar_label",
            options=list(label_map.keys()),
            horizontal=True,
            label_visibility="collapsed",
            key="subcase_translate_grammar",
        )
        selected_sub = label_map[picked]

    else:
        label_map = {
            "문장(표현) 다듬기": "rewrite_polish",
        }
        picked = st.radio(
            "subcase_polish_label",
            options=list(label_map.keys()),
            horizontal=True,
            label_visibility="collapsed",
            key="subcase_polish",
        )
        selected_sub = label_map[picked]

    # -------------------------
    # 3) Sidebar (case별 기본 옵션)
    # -------------------------
    with st.sidebar:
        st.header("⚙️ 옵션 설정")

        # 공통: 출력 언어
        prompt_language = st.selectbox(
            "출력 언어", options=["한국어", "영어"], index=0, key="prompt_language"
        )
        prompt_lang_code = "ko" if prompt_language == "한국어" else "en"

        st.divider()
        st.subheader("기본 옵션")

        # defaults
        thinking_style = "데이터 기반 사고"
        answer_tone = "공식 문체"

        translation_style = "natural"
        translation_tone = "neutral"

        grammar_scope = "grammar_vocab_only"
        grammar_tone = "keep"

        polish_freedom = "medium"
        polish_tone = "professional"

        length_mode = "default"

        # case별 기본 옵션 UI
        if top_case_id == "1":
            thinking_style = st.selectbox(
                "사고 방식 설정", ["데이터 기반 사고", "비판적", "창의적"], index=0, key="thinking_style"
            )
            answer_tone = st.selectbox(
                "답변 톤", ["공식 문체", "친근하게", "간결하게"], index=0, key="answer_tone"
            )

        elif top_case_id == "2" and selected_sub == "translate":
            style_ui = st.selectbox(
                "의역/자연스러움 정도",
                ["직역(정확)", "균형", "의역(자연)"],
                index=1,
                key="translation_style_ui",
            )
            translation_style = {"직역(정확)": "literal", "균형": "balanced", "의역(자연)": "natural"}[style_ui]

            tone_ui = st.selectbox(
                "번역 톤",
                ["기본", "공식", "친근"],
                index=0,
                key="translation_tone_ui",
            )
            translation_tone = {"기본": "neutral", "공식": "formal", "친근": "casual"}[tone_ui]

            # 번역일 때는 기존 thinking/tone는 의미 없으니 고정값 유지(빈값도 가능)
            thinking_style = ""
            answer_tone = ""

        elif top_case_id == "2" and selected_sub == "grammar_correction":
            scope_ui = st.radio(
                "교정 범위",
                ["문법/어휘만 개선(문체/말투 유지)", "말투/문체까지 개선(톤 변경 허용)"],
                horizontal=False,
                key="grammar_scope_ui",
            )
            grammar_scope = {
                "문법/어휘만 개선(문체/말투 유지)": "grammar_vocab_only",
                "말투/문체까지 개선(톤 변경 허용)": "include_tone",
            }[scope_ui]

            if grammar_scope == "include_tone":
                tone_ui = st.selectbox(
                    "원하는 톤",
                    ["기존 유지", "공식", "친근", "전문적으로", "간결하게"],
                    index=0,
                    key="grammar_tone_ui",
                )
                grammar_tone = {
                    "기존 유지": "keep",
                    "공식": "formal",
                    "친근": "casual",
                    "전문적으로": "professional",
                    "간결하게": "concise",
                }[tone_ui]
            else:
                grammar_tone = "keep"

            thinking_style = ""
            answer_tone = ""

        elif top_case_id == "3" and selected_sub == "rewrite_polish":
            freedom_ui = st.selectbox(
                "문체 변화 자유도",
                ["낮음(원문 최대 유지)", "중간(자연스럽게 다듬기)", "높음(상당히 재작성 허용)"],
                index=1,
                key="polish_freedom_ui",
            )
            polish_freedom = {
                "낮음(원문 최대 유지)": "low",
                "중간(자연스럽게 다듬기)": "medium",
                "높음(상당히 재작성 허용)": "high",
            }[freedom_ui]

            tone_ui = st.selectbox(
                "원하는 톤",
                ["기존 유지", "전문적으로", "공식", "친근", "간결하게"],
                index=1,
                key="polish_tone_ui",
            )
            polish_tone = {
                "기존 유지": "keep",
                "전문적으로": "professional",
                "공식": "formal",
                "친근": "casual",
                "간결하게": "concise",
            }[tone_ui]

            thinking_style = ""
            answer_tone = ""

        three_variants = False
        if top_case_id == "2" or top_case_id == "3":
            three_variants = st.checkbox(
                "3가지 버전 제시",
                value=True,
                help="3가지 버전의 응답을 제시하도록 지시하여 더 많은 선택 옵션을 얻을 수 있습니다.",
                key="three_variants",
            )
        else:
            # 1번 케이스에서만 '답변 길이' 유지
            length_ui = st.selectbox("답변 길이", ["짧게", "기본", "길게"], index=1, key="length_ui")
            length_map = {"짧게": "short", "기본": "default", "길게": "long"}
            length_mode = length_map[length_ui]

        st.divider()
        st.subheader("고급 옵션")

        if top_case_id == "1":
            provide_sources = st.checkbox(
                "환각 문제 개선",
                value=True,
                help="답변에 반드시 출처를 포함하도록 지시하여 환각(hallucination) 문제를 개선할 수 있습니다.",
                key="provide_sources",
            )
        elif top_case_id == "2" or top_case_id == "3":
            provide_sources = st.checkbox(
                "환각 문제 개선",
                value=False,
                help="답변에 반드시 출처를 포함하도록 지시하여 환각(hallucination) 문제를 개선할 수 있습니다.",
                key="provide_sources",
            )

        allow_clarifying_questions = st.checkbox(
            "답변 전 질문 허용",
            value=False,
            help="역질문을 통해 모호한 사항을 해결하고, 사용자의 의도를 보다 정확히 반영할 수 있도록 지시합니다.",
            key="allow_clarifying_questions",
        )
        avoid_speculation = st.checkbox(
            "추측 금지",
            value=False,
            help="명확한 근거나 출처가 없는 답변을 하지 않도록 지시합니다.",
            key="avoid_speculation",
        )

        st.divider()
        st.subheader("역할 / 독자 / 범위 (선택사항)")
        role_domain = none_if_blank_or_none_str(st.text_input("Role domain (optional)", value="", key="role_domain"))
        audience = none_if_blank_or_none_str(st.text_input("Audience (optional)", value="", key="audience"))
        time_range = none_if_blank_or_none_str(st.text_input("Time range (optional)", value="", key="time_range"))

        st.divider()
        st.subheader("출력 구조 (선택사항)")
        output_structure = st.text_area("Output formatting constraint (optional)", value="", height=110, key="output_structure")
        output_structure = none_if_blank_or_none_str(output_structure)

    # -------------------------
    # 4) USER_INPUT
    # -------------------------
    st.markdown("### 📝 사용자 입력 ")
    user_input = st.text_area(
        "USER_INPUT",
        placeholder="여기에 질문을 입력하세요...",
        height=220,
        label_visibility="collapsed",
        key="user_input",
    )

    gen = st.button("프롬프트 생성", type="primary", use_container_width=True)

    st.markdown("### 📄 생성된 프롬프트")
    out_placeholder = st.empty()
    out_placeholder.code("", language="")

    # Goal: auto
    if top_case_id == "1":
        goal = "If no goal is specified, analyze USER_INPUT and automatically generate a clear, specific, actionable goal."
    elif top_case_id == "2":
        if selected_sub == "translate":
            goal = "Translate USER_INPUT according to the specified translation preferences."
        elif selected_sub == "grammar_correction":
            goal = "Correct grammar and improve expressions in USER_INPUT according to the specified scope, while preserving the original meaning and intent."
    elif top_case_id == "3":
        goal = "Rewrite and polish USER_INPUT to improve clarity, naturalness, and professionalism, without changing its original meaning."

    if gen:
        if not user_input.strip():
            st.error("USER_INPUT이 비어 있습니다.")
            return
        if not (MODEL_URL and MODEL_NAME and BEARER_TOKEN):
            st.error("config.json에 MODEL_URL / MODEL_NAME / BEARER_TOKEN 설정이 필요합니다.")
            return

        cfg_obj = PromptConfig(
            top_case_id=top_case_id,
            role_domain=role_domain,
            thinking_style=thinking_style,
            answer_tone=answer_tone,
            goal=goal,
            audience=audience,
            time_range=time_range,
            provide_sources=provide_sources,
            avoid_speculation=avoid_speculation,
            output_structure=output_structure,
            prompt_language=prompt_lang_code,
            length_mode=length_mode,
            user_input=user_input.strip(),
            # case-specific
            translation_style=translation_style,
            translation_tone=translation_tone,
            grammar_scope=grammar_scope,
            grammar_tone=grammar_tone,
            polish_freedom=polish_freedom,
            polish_tone=polish_tone,
        )

        messages = generate_prompt(cfg_obj, selected_sub)

        acc = ""
        try:
            for delta in call_llm_stream(
                messages=messages,
                model_url=MODEL_URL,
                model_name=MODEL_NAME,
                bearer_token=BEARER_TOKEN,
                asms_header=ASMS_HEADER,
            ):
                acc += delta
                out_placeholder.code(acc, language="")

            user_block = build_user_input_section(user_input, prompt_lang_code)
            acc_final = acc + user_block + build_suffix(
                        provide_sources,
                        avoid_speculation,
                        allow_clarifying_questions,
                        three_variants,
                        prompt_lang_code,
                    )
            out_placeholder.code(acc_final, language="")

        except Exception as e:
            st.error(f"Streaming error: {e}")


if __name__ == "__main__":
    main()