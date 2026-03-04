# ui_i18n.py

I18N = {
    "ko": {
        # ===== header / sections =====
        "title": "🧩 Prompt Generator Demo",
        "case_select": "#### Case 선택",
        "subcase_select": "##### 세부 Case",

        "sidebar_header": "⚙️ 옵션 설정",
        "basic_opt": "기본 옵션",
        "advanced_opt": "고급 옵션",

        "output_lang": "출력 언어",
        "lang_ko": "한국어",
        "lang_en": "영어",

        "role_scope": "역할 / 독자 / 범위 (선택사항)",
        "output_structure": "출력 구조 (선택사항)",

        "user_input_header": "### 📝 사용자 입력",
        "user_input_placeholder": "여기에 질문을 입력하세요...",

        "gen_btn": "프롬프트 생성",
        "generated_prompt": "### 📄 생성된 프롬프트",

        "err_empty_input": "USER_INPUT이 비어 있습니다.",
        "err_missing_config": "MODEL_URL / MODEL_NAME / BEARER_TOKEN 설정이 필요합니다.",

        "floating_btn": "🔗 바로 질문하러 갈까요?",

        # ===== cases =====
        "case_options": [
            "1. 🔎 정보 탐색 및 정리",
            "2. ✍️ 번역 및 문법 교정",
            "3. ✨ 문장(표현) 다듬기",
        ],
        "info_subcases": ["빠른 정보 탐색", "비교 탐색", "시장/트렌드 분석", "의사 결정"],
        "tg_subcases": ["번역", "문법 교정"],
        "polish_subcases": ["문장(표현) 다듬기"],

        # ===== sidebar labels =====
        "thinking_style": "사고 방식 설정",
        "answer_tone": "답변 톤",
        "translation_style": "의역/자연스러움 정도",
        "translation_tone": "번역 톤",
        "grammar_scope": "교정 범위",
        "desired_tone": "원하는 톤",
        "polish_freedom": "문체 변화 자유도",
        "hallucination": "환각 문제 개선",
        "clarify": "답변 전 질문 허용",
        "no_spec": "추측 금지",
        "length": "답변 길이",
        "three_variants": "3가지 버전 제시",

        # ===== sidebar options / maps =====
        "thinking_style_options": ["데이터 기반 사고", "비판적", "창의적"],
        "answer_tone_options": ["공식 문체", "친근하게", "간결하게"],

        "translation_style_options": ["직역(정확)", "균형", "의역(자연)"],
        "translation_style_map": {
            "직역(정확)": "literal",
            "균형": "balanced",
            "의역(자연)": "natural",
        },

        "translation_tone_options": ["기본", "공식", "친근"],
        "translation_tone_map": {
            "기본": "neutral",
            "공식": "formal",
            "친근": "casual",
        },

        "grammar_scope_options": [
            "문법/어휘만 개선(문체/말투 유지)",
            "말투/문체까지 개선(톤 변경 허용)",
        ],
        "grammar_scope_map": {
            "문법/어휘만 개선(문체/말투 유지)": "grammar_vocab_only",
            "말투/문체까지 개선(톤 변경 허용)": "include_tone",
        },

        "desired_tone_options": ["기존 유지", "공식", "친근", "전문적으로", "간결하게"],
        "desired_tone_map": {
            "기존 유지": "keep",
            "공식": "formal",
            "친근": "casual",
            "전문적으로": "professional",
            "간결하게": "concise",
        },

        "polish_freedom_options": [
            "낮음(원문 최대 유지)",
            "중간(자연스럽게 다듬기)",
            "높음(상당히 재작성 허용)",
        ],
        "polish_freedom_map": {
            "낮음(원문 최대 유지)": "low",
            "중간(자연스럽게 다듬기)": "medium",
            "높음(상당히 재작성 허용)": "high",
        },

        "desired_tone_options_polish": ["기존 유지", "전문적으로", "공식", "친근", "간결하게"],
        "desired_tone_map_polish": {
            "기존 유지": "keep",
            "전문적으로": "professional",
            "공식": "formal",
            "친근": "casual",
            "간결하게": "concise",
        },

        "length_options": ["짧게", "기본", "길게"],
        "length_map": {"짧게": "short", "기본": "default", "길게": "long"},

        # ===== helps =====
        "three_variants_help": "3가지 버전의 응답을 제시하여 더 많은 선택지를 제공합니다.",
        "hallucination_help": "답변에 출처를 포함하도록 요구해 환각(hallucination) 가능성을 낮춥니다.",
        "clarify_help": "입력이 모호하면 먼저 역질문을 하도록 지시합니다.",
        "no_spec_help": "명확한 근거/출처 없이 추측하지 않도록 지시합니다.",

        # ===== text inputs =====
        "role_domain": "Role domain (optional)",
        "audience": "Audience (optional)",
        "time_range": "Time range (optional)",
        "output_format_constraint": "Output formatting constraint (optional)",

        # ===== error prefix =====
        "streaming_error_prefix": "Streaming error: ",
    },

    "en": {
        # ===== header / sections =====
        "title": "🧩 Prompt Generator Demo",
        "case_select": "#### Select a Case",
        "subcase_select": "##### Select a Sub-case",

        "sidebar_header": "⚙️ Options",
        "basic_opt": "Basic options",
        "advanced_opt": "Advanced options",

        "output_lang": "Output language",
        "lang_ko": "Korean",
        "lang_en": "English",

        "role_scope": "Role / Audience / Scope (Optional)",
        "output_structure": "Output formatting (Optional)",

        "user_input_header": "### 📝 User input",
        "user_input_placeholder": "Type your question here...",

        "gen_btn": "Generate prompt",
        "generated_prompt": "### 📄 Generated prompt",

        "err_empty_input": "USER_INPUT is empty.",
        "err_missing_config": "MODEL_URL / MODEL_NAME / BEARER_TOKEN must be set.",

        "floating_btn": "🔗 Ask a question now",

        # ===== cases =====
        "case_options": [
            "1. 🔎 Research & Summarize",
            "2. ✍️ Translation & Grammar",
            "3. ✨ Rewrite & Polish",
        ],
        "info_subcases": ["Quick lookup", "Comparison", "Market/Trend analysis", "Decision brief"],
        "tg_subcases": ["Translation", "Grammar correction"],
        "polish_subcases": ["Rewrite & polish"],

        # ===== sidebar labels =====
        "thinking_style": "Thinking style",
        "answer_tone": "Answer tone",
        "translation_style": "Translation literalness",
        "translation_tone": "Translation tone",
        "grammar_scope": "Correction scope",
        "desired_tone": "Desired tone",
        "polish_freedom": "Rewrite freedom",
        "hallucination": "Reduce hallucinations",
        "clarify": "Allow clarifying questions",
        "no_spec": "No speculation",
        "length": "Answer length",
        "three_variants": "Show 3 variants",

        # ===== sidebar options / maps =====
        "thinking_style_options": ["Data-driven", "Critical", "Creative"],
        "answer_tone_options": ["Formal", "Friendly", "Concise"],

        "translation_style_options": ["Literal (accurate)", "Balanced", "Free (natural)"],
        "translation_style_map": {
            "Literal (accurate)": "literal",
            "Balanced": "balanced",
            "Free (natural)": "natural",
        },

        "translation_tone_options": ["Neutral", "Formal", "Casual"],
        "translation_tone_map": {
            "Neutral": "neutral",
            "Formal": "formal",
            "Casual": "casual",
        },

        "grammar_scope_options": [
            "Grammar/vocabulary only (keep tone)",
            "Include tone/style improvement",
        ],
        "grammar_scope_map": {
            "Grammar/vocabulary only (keep tone)": "grammar_vocab_only",
            "Include tone/style improvement": "include_tone",
        },

        "desired_tone_options": ["Keep original", "Formal", "Casual", "Professional", "Concise"],
        "desired_tone_map": {
            "Keep original": "keep",
            "Formal": "formal",
            "Casual": "casual",
            "Professional": "professional",
            "Concise": "concise",
        },

        "polish_freedom_options": [
            "Low (preserve original)",
            "Medium (natural polish)",
            "High (major rewrite allowed)",
        ],
        "polish_freedom_map": {
            "Low (preserve original)": "low",
            "Medium (natural polish)": "medium",
            "High (major rewrite allowed)": "high",
        },

        "desired_tone_options_polish": ["Keep original", "Professional", "Formal", "Casual", "Concise"],
        "desired_tone_map_polish": {
            "Keep original": "keep",
            "Professional": "professional",
            "Formal": "formal",
            "Casual": "casual",
            "Concise": "concise",
        },

        "length_options": ["Short", "Default", "Long"],
        "length_map": {"Short": "short", "Default": "default", "Long": "long"},

        # ===== helps =====
        "three_variants_help": "Generate three response variants to provide more options.",
        "hallucination_help": "Require sources/evidence to reduce hallucinations.",
        "clarify_help": "Ask follow-up questions if the input is ambiguous.",
        "no_spec_help": "Avoid unsupported claims or guesses.",

        # ===== text inputs =====
        "role_domain": "Role domain (optional)",
        "audience": "Audience (optional)",
        "time_range": "Time range (optional)",
        "output_format_constraint": "Output formatting constraint (optional)",

        # ===== error prefix =====
        "streaming_error_prefix": "Streaming error: ",
    },
}