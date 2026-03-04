#!/usr/bin/env python
# app.py
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Iterator

from ui_i18n import I18N
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

    # -------------------------
    # UI language toggle (KR/EN)
    # -------------------------
    if "ui_lang_toggle" not in st.session_state:
        st.session_state.ui_lang_toggle = False  # False=KR, True=EN

    ui_lang = "en" if st.session_state.ui_lang_toggle else "ko"
    T = I18N[ui_lang]

    left, right = st.columns([0.88, 0.12], vertical_alignment="center")

    with left:
        st.title(T["title"])

    with right:
        st.markdown(
            f"<div style='text-align:center; font-size:12px; opacity:.75; white-space:nowrap;'>"
            f"{'EN' if ui_lang=='en' else 'KR'}</div>",
            unsafe_allow_html=True
        )

        a, b, c = st.columns([0.25, 0.50, 0.25], gap="small")
        with b:
            st.toggle(label="UI language", key="ui_lang_toggle", label_visibility="collapsed")

    st.markdown(
        """
        <style>
        /* ===== Radio -> Tab-like UI ===== */
        div[role="radiogroup"] { gap: 8px; }
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
        {T["floating_btn"]}
        </a>
        """,
        unsafe_allow_html=True,
    )

    # -------------------------
    # 1) Top-level case 선택
    # -------------------------
    st.markdown(T["case_select"])
    top_case = st.selectbox(
        label="Top-level case",
        options=T["case_options"],
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
            "length_ui",
        ]:
            if k in st.session_state:
                del st.session_state[k]
        st.session_state.prev_top_case = top_case

    # -------------------------
    # 2) 세부 Case 선택
    # -------------------------
    st.markdown(T["subcase_select"])

    if top_case_id == "1":
        label_map = dict(
            zip(
                T["info_subcases"],
                ["quick_info", "comparison", "market_trend", "decision_brief"],
            )
        )
        picked = st.radio(
            "subcase_info_label",
            options=list(label_map.keys()),
            horizontal=True,
            label_visibility="collapsed",
            key="subcase_info",
        )
        selected_sub = label_map[picked]

    elif top_case_id == "2":
        label_map = dict(zip(T["tg_subcases"], ["translate", "grammar_correction"]))
        picked = st.radio(
            "subcase_translate_grammar_label",
            options=list(label_map.keys()),
            horizontal=True,
            label_visibility="collapsed",
            key="subcase_translate_grammar",
        )
        selected_sub = label_map[picked]

    else:
        label_map = {T["polish_subcases"][0]: "rewrite_polish"}
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
        st.header(T["sidebar_header"])

        # 공통: 출력 언어 (LLM 출력 언어; UI 언어와 별개)
        prompt_language = st.selectbox(
            T["output_lang"],
            options=[T["lang_ko"], T["lang_en"]],
            index=0,
            key="prompt_language",
        )
        prompt_lang_code = "ko" if prompt_language == T["lang_ko"] else "en"

        st.divider()
        st.subheader(T["basic_opt"])

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
                T["thinking_style"],
                options=T["thinking_style_options"],
                index=0,
                key="thinking_style",
            )
            answer_tone = st.selectbox(
                T["answer_tone"],
                options=T["answer_tone_options"],
                index=0,
                key="answer_tone",
            )

        elif top_case_id == "2" and selected_sub == "translate":
            style_ui = st.selectbox(
                T["translation_style"],
                options=T["translation_style_options"],
                index=1,
                key="translation_style_ui",
            )
            # map UI label -> internal code
            translation_style = T["translation_style_map"][style_ui]

            tone_ui = st.selectbox(
                T["translation_tone"],
                options=T["translation_tone_options"],
                index=0,
                key="translation_tone_ui",
            )
            translation_tone = T["translation_tone_map"][tone_ui]

            thinking_style = ""
            answer_tone = ""

        elif top_case_id == "2" and selected_sub == "grammar_correction":
            scope_ui = st.radio(
                T["grammar_scope"],
                options=T["grammar_scope_options"],
                horizontal=False,
                key="grammar_scope_ui",
            )
            grammar_scope = T["grammar_scope_map"][scope_ui]

            if grammar_scope == "include_tone":
                tone_ui = st.selectbox(
                    T["desired_tone"],
                    options=T["desired_tone_options"],
                    index=0,
                    key="grammar_tone_ui",
                )
                grammar_tone = T["desired_tone_map"][tone_ui]
            else:
                grammar_tone = "keep"

            thinking_style = ""
            answer_tone = ""

        elif top_case_id == "3" and selected_sub == "rewrite_polish":
            freedom_ui = st.selectbox(
                T["polish_freedom"],
                options=T["polish_freedom_options"],
                index=1,
                key="polish_freedom_ui",
            )
            polish_freedom = T["polish_freedom_map"][freedom_ui]

            tone_ui = st.selectbox(
                T["desired_tone"],
                options=T["desired_tone_options_polish"],
                index=1,
                key="polish_tone_ui",
            )
            polish_tone = T["desired_tone_map_polish"][tone_ui]

            thinking_style = ""
            answer_tone = ""

        three_variants = False
        if top_case_id == "2" or top_case_id == "3":
            three_variants = st.checkbox(
                T["three_variants"],
                value=True,
                help=T["three_variants_help"],
                key="three_variants",
            )
        else:
            length_ui = st.selectbox(
                T["length"],
                options=T["length_options"],
                index=1,
                key="length_ui",
            )
            length_mode = T["length_map"][length_ui]

        st.divider()
        st.subheader(T["advanced_opt"])

        # provide_sources default differs by case (keep your behavior)
        if top_case_id == "1":
            provide_sources = st.checkbox(
                T["hallucination"],
                value=True,
                help=T["hallucination_help"],
                key="provide_sources",
            )
        else:
            provide_sources = st.checkbox(
                T["hallucination"],
                value=False,
                help=T["hallucination_help"],
                key="provide_sources",
            )

        allow_clarifying_questions = st.checkbox(
            T["clarify"],
            value=False,
            help=T["clarify_help"],
            key="allow_clarifying_questions",
        )
        avoid_speculation = st.checkbox(
            T["no_spec"],
            value=False,
            help=T["no_spec_help"],
            key="avoid_speculation",
        )

        st.divider()
        st.subheader(T["role_scope"])
        role_domain = none_if_blank_or_none_str(
            st.text_input(T["role_domain"], value="", key="role_domain")
        )
        audience = none_if_blank_or_none_str(
            st.text_input(T["audience"], value="", key="audience")
        )
        time_range = none_if_blank_or_none_str(
            st.text_input(T["time_range"], value="", key="time_range")
        )

        st.divider()
        st.subheader(T["output_structure"])
        output_structure = st.text_area(
            T["output_format_constraint"],
            value="",
            height=110,
            key="output_structure",
        )
        output_structure = none_if_blank_or_none_str(output_structure)

    # -------------------------
    # 4) USER_INPUT
    # -------------------------
    st.markdown(T["user_input_header"])
    user_input = st.text_area(
        "USER_INPUT",
        placeholder=T["user_input_placeholder"],
        height=220,
        label_visibility="collapsed",
        key="user_input",
    )

    gen = st.button(T["gen_btn"], type="primary", use_container_width=True)

    st.markdown(T["generated_prompt"])
    out_placeholder = st.empty()
    out_placeholder.code("", language="")

    # Goal: auto (these are for LLM prompt generation; keep as-is English)
    if top_case_id == "1":
        goal = "If no goal is specified, analyze USER_INPUT and automatically generate a clear, specific, actionable goal."
    elif top_case_id == "2":
        if selected_sub == "translate":
            goal = "Translate USER_INPUT according to the specified translation preferences."
        elif selected_sub == "grammar_correction":
            goal = "Correct grammar and improve expressions in USER_INPUT according to the specified scope, while preserving the original meaning and intent."
    else:
        goal = "Rewrite and polish USER_INPUT to improve clarity, naturalness, and professionalism, without changing its original meaning."

    if gen:
        if not user_input.strip():
            st.error(T["err_empty_input"])
            return
        if not (MODEL_URL and MODEL_NAME and BEARER_TOKEN):
            st.error(T["err_missing_config"])
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
            st.error(f"{T['streaming_error_prefix']}{e}")


if __name__ == "__main__":
    main()