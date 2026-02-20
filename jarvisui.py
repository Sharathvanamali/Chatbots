import streamlit as st
import ollama
import json
import time
import os
import tempfile
import base64
import hashlib
from datetime import datetime
from pathlib import Path

# ── Optional heavy deps ──────────────────────────────────────────────────────
try:
    import speech_recognition as sr
    VOICE_OK = True
except ImportError:
    VOICE_OK = False

try:
    import pyttsx3
    TTS_OK = True
except ImportError:
    TTS_OK = False

try:
    import fitz  # PyMuPDF
    PDF_OK = True
except ImportError:
    PDF_OK = False

try:
    from deep_translator import GoogleTranslator
    TRANS_OK = True
except ImportError:
    TRANS_OK = False

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="JargonBot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

:root {
  --bg:       #04040a;
  --surface:  #0c0c18;
  --panel:    #10101f;
  --border:   #1e1e3a;
  --accent:   #7c3aed;
  --accent2:  #06b6d4;
  --accent3:  #f59e0b;
  --text:     #e2e8f0;
  --muted:    #64748b;
  --user-bg:  #1a1030;
  --bot-bg:   #0d1a2e;
  --think-bg: #0a1a0a;
  --think-border: #166534;
  --glow:     0 0 20px rgba(124,58,237,.35);
}

* { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  font-family: 'Syne', sans-serif;
  color: var(--text);
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stToolbar"] { display: none; }

/* ─── TOP NAV ─────────────────────────────────────────────────── */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 28px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 999;
}
.logo {
  font-family: 'Space Mono', monospace;
  font-size: 1.4rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.logo span { color: var(--accent3); -webkit-text-fill-color: var(--accent3); }
.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(6,182,212,.12);
  border: 1px solid rgba(6,182,212,.3);
  border-radius: 20px;
  padding: 4px 12px;
  font-size: .75rem;
  color: var(--accent2);
  font-family: 'Space Mono', monospace;
}
.status-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 8px #22c55e;
  animation: pulse 1.8s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }

/* ─── SIDEBAR ─────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] .stSelectbox > div > div {
  background: var(--panel) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
}

/* ─── CHAT AREA ───────────────────────────────────────────────── */
.chat-wrapper {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px 16px 140px;
}

.msg-row { display: flex; gap: 12px; margin-bottom: 20px; animation: fadeUp .3s ease; }
@keyframes fadeUp { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }

.msg-row.user { flex-direction: row-reverse; }

.avatar {
  width: 38px; height: 38px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem; flex-shrink: 0;
  font-family: 'Space Mono', monospace;
}
.avatar.bot  { background: linear-gradient(135deg,var(--accent),var(--accent2)); box-shadow: var(--glow); }
.avatar.user { background: var(--user-bg); border: 1px solid var(--border); }

.bubble {
  max-width: 78%;
  padding: 14px 18px;
  border-radius: 16px;
  line-height: 1.65;
  font-size: .93rem;
}
.bubble.bot {
  background: var(--bot-bg);
  border: 1px solid var(--border);
  border-top-left-radius: 4px;
}
.bubble.user {
  background: var(--user-bg);
  border: 1px solid rgba(124,58,237,.3);
  border-top-right-radius: 4px;
  text-align: right;
}

/* ─── THINKING BOX ────────────────────────────────────────────── */
.think-box {
  background: var(--think-bg);
  border: 1px solid var(--think-border);
  border-radius: 10px;
  padding: 10px 14px;
  margin-bottom: 10px;
  font-family: 'Space Mono', monospace;
  font-size: .75rem;
  color: #86efac;
  cursor: pointer;
}
.think-title {
  display: flex; align-items: center; gap: 8px;
  font-weight: 700; margin-bottom: 6px;
  color: #4ade80;
}
.think-content { opacity:.75; white-space: pre-wrap; }

/* ─── FEATURE BADGES ──────────────────────────────────────────── */
.badge {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 3px 9px; border-radius: 20px;
  font-size: .7rem; font-family: 'Space Mono', monospace;
  margin: 2px;
}
.badge.active  { background:rgba(34,197,94,.15); border:1px solid rgba(34,197,94,.4); color:#4ade80; }
.badge.inactive{ background:rgba(100,116,139,.1); border:1px solid var(--border); color:var(--muted); }

/* ─── INPUT AREA ──────────────────────────────────────────────── */
.stTextArea textarea {
  background: var(--panel) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  color: var(--text) !important;
  font-family: 'Syne', sans-serif !important;
  font-size: .93rem !important;
  resize: none !important;
}
.stTextArea textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 2px rgba(124,58,237,.25) !important;
}

/* ─── BUTTONS ─────────────────────────────────────────────────── */
.stButton > button {
  background: linear-gradient(135deg, var(--accent), #5b21b6) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 10px !important;
  font-family: 'Space Mono', monospace !important;
  font-weight: 700 !important;
  font-size: .8rem !important;
  letter-spacing: .05em !important;
  padding: 10px 20px !important;
  transition: all .2s !important;
}
.stButton > button:hover {
  transform: translateY(-1px) !important;
  box-shadow: var(--glow) !important;
}

/* code blocks inside bubbles */
.bubble pre { background:#1e1e3a; border-radius:8px; padding:12px; overflow-x:auto; }
.bubble code { font-family:'Space Mono',monospace; font-size:.82rem; color:#93c5fd; }

/* scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }

/* Metrics */
[data-testid="stMetric"] {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px !important;
}
[data-testid="stMetricValue"] { color: var(--accent2) !important; font-family:'Space Mono',monospace; }

/* File uploader */
[data-testid="stFileUploader"] {
  background: var(--panel) !important;
  border: 1px dashed var(--border) !important;
  border-radius: 12px !important;
}

/* Expander */
details { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; }
summary { color: var(--accent2) !important; font-family:'Space Mono',monospace; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "messages": [],
        "model": "gemma3:latest",
        "lang": "en",
        "voice_enabled": False,
        "thinking_visible": True,
        "pdf_context": "",
        "total_tokens": 0,
        "session_start": datetime.now().strftime("%H:%M"),
        "msg_count": 0,
        "last_think": "",
        "last_response": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Helpers ───────────────────────────────────────────────────────────────────
LANG_MAP = {
    "English":"en","Tamil":"ta","Hindi":"hi","Spanish":"es",
    "French":"fr","German":"de","Japanese":"ja","Arabic":"ar",
    "Chinese":"zh-CN","Portuguese":"pt","Korean":"ko","Russian":"ru",
}

JARGON_SYSTEM = """You are JargonBot — an elite AI assistant that ALWAYS:
1. SHOWS THINKING: Wrap your chain-of-thought inside <think>...</think> tags BEFORE answering.
2. ANSWERS IN 4 WORDS: Your final answer (outside <think>) must be exactly 4 words.
3. USES JARGON: Every word should be technical, domain-specific, or sophisticated jargon.
4. CODES ACCURATELY: When asked to code, place code inside <think> as full implementation, then summarize in 4-word jargon answer.
5. BE MULTILINGUAL: If user writes in another language, respond in that language, still in jargon, still 4 words.
6. PRECISION OVER VERBOSITY: You are concise by design. 4 words. Always.

Format STRICTLY:
<think>
[Your detailed reasoning, analysis, full code if needed — all here]
</think>
[EXACTLY 4 JARGON WORDS]
"""

def get_ollama_models():
    try:
        models = ollama.list()
        return [m.model for m in models.models] if models.models else ["gemma3"]
    except:
        return ["gemma3:latest"]

def extract_think_and_answer(text: str):
    think = ""
    answer = text
    if "<think>" in text and "</think>" in text:
        start = text.index("<think>") + 7
        end   = text.index("</think>")
        think  = text[start:end].strip()
        answer = text[end+8:].strip()
    return think, answer

def stream_response(prompt: str, history: list, pdf_ctx: str = ""):
    sys_prompt = JARGON_SYSTEM
    if pdf_ctx:
        sys_prompt += f"\n\nPDF CONTEXT:\n{pdf_ctx[:4000]}"

    messages = [{"role": "system", "content": sys_prompt}]
    for h in history[-12:]:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": prompt})

    full = ""
    try:
        for chunk in ollama.chat(
            model=st.session_state.model,
            messages=messages,
            stream=True,
        ):
            delta = chunk.message.content or ""
            full += delta
            yield delta, full
    except Exception as e:
        err = f"⚠ Ollama error: {e}\n\nMake sure `ollama serve` is running and model is pulled."
        yield err, err

def read_pdf(uploaded_file) -> str:
    if not PDF_OK:
        return "PyMuPDF not installed. Run: pip install pymupdf"
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            f.write(uploaded_file.read())
            tmp = f.name
        doc = fitz.open(tmp)
        text = "\n\n".join(page.get_text() for page in doc)
        doc.close()
        os.unlink(tmp)
        return text
    except Exception as e:
        return f"PDF read error: {e}"

def translate_text(text: str, target: str) -> str:
    if not TRANS_OK or target == "en":
        return text
    try:
        return GoogleTranslator(source="auto", target=target).translate(text)
    except:
        return text

def voice_to_text() -> str:
    if not VOICE_OK:
        return ""
    r = sr.Recognizer()
    with sr.Microphone() as src:
        r.adjust_for_ambient_noise(src, duration=0.5)
        audio = r.listen(src, timeout=5)
    try:
        return r.recognize_google(audio)
    except:
        return ""

def speak_text(text: str):
    if not TTS_OK:
        return
    engine = pyttsx3.init()
    engine.setProperty("rate", 165)
    engine.say(text)
    engine.runAndWait()

def render_message(role: str, content: str, think: str = "", idx: int = 0):
    if role == "user":
        st.markdown(f"""
        <div class="msg-row user">
          <div class="avatar user">U</div>
          <div class="bubble user">{content}</div>
        </div>""", unsafe_allow_html=True)
    else:
        think_html = ""
        if think and st.session_state.thinking_visible:
            think_safe = think.replace("<","&lt;").replace(">","&gt;")
            think_html = f"""
            <div class="think-box">
              <div class="think-title">⚡ COGNITIVE PROCESS <span style="font-size:.65rem;opacity:.6">#{idx}</span></div>
              <div class="think-content">{think_safe[:1200]}{"…" if len(think_safe)>1200 else ""}</div>
            </div>"""

        answer_html = content.replace("<","&lt;").replace(">","&gt;") if content else ""
        st.markdown(f"""
        <div class="msg-row">
          <div class="avatar bot">J</div>
          <div class="bubble bot">{think_html}<div style="font-weight:700;font-size:1rem;color:#e2e8f0">{answer_html}</div></div>
        </div>""", unsafe_allow_html=True)

# ── Top bar ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
  <div class="logo">Jargon<span>Bot</span></div>
  <div class="status-pill"><div class="status-dot"></div>GEMMA·3 ACTIVE</div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙ CONFIGURATION")

    models = get_ollama_models()
    preferred = next((m for m in models if "gemma3:latest" in m or "gemma3:latest" in m), models[0] if models else "gemma3:latest")
    sel_model = st.selectbox("🤖 Model", models, index=models.index(preferred) if preferred in models else 0)
    st.session_state.model = sel_model

    st.markdown("---")
    st.markdown("### 🌍 LANGUAGE")
    lang_name = st.selectbox("Output Language", list(LANG_MAP.keys()))
    st.session_state.lang = LANG_MAP[lang_name]

    st.markdown("---")
    st.markdown("### 🎛 FEATURES")
    st.session_state.thinking_visible = st.toggle("🧠 Show Thinking Process", value=True)
    st.session_state.voice_enabled    = st.toggle("🔊 Text-to-Speech", value=False)

    st.markdown("---")
    st.markdown("### 📄 PDF READER")
    pdf_file = st.file_uploader("Upload PDF", type=["pdf"])
    if pdf_file:
        with st.spinner("Parsing PDF…"):
            ctx = read_pdf(pdf_file)
            st.session_state.pdf_context = ctx
        word_count = len(ctx.split())
        st.success(f"✅ {word_count:,} words loaded")
        with st.expander("Preview"):
            st.text(ctx[:500] + "…" if len(ctx) > 500 else ctx)
    if st.session_state.pdf_context:
        if st.button("🗑 Clear PDF"):
            st.session_state.pdf_context = ""
            st.rerun()

    st.markdown("---")
    st.markdown("### 🎤 VOICE INPUT")
    if VOICE_OK:
        if st.button("🎙 Record (5s)"):
            with st.spinner("Listening…"):
                text = voice_to_text()
            if text:
                st.success(f"Heard: {text}")
                st.session_state["voice_input"] = text
            else:
                st.error("No speech detected")
    else:
        st.caption("Install `speechrecognition` + `pyaudio` for voice")

    st.markdown("---")
    st.markdown("### 📊 SESSION STATS")
    c1, c2 = st.columns(2)
    c1.metric("Messages", st.session_state.msg_count)
    c2.metric("Session", st.session_state.session_start)

    st.markdown("---")
    if st.button("🗑 Clear History"):
        st.session_state.messages  = []
        st.session_state.msg_count = 0
        st.session_state.pdf_context = ""
        st.rerun()

    st.markdown("---")
    # Feature availability badges
    st.markdown("**CAPABILITY STATUS**")
    feats = [
        ("Voice I/O", VOICE_OK),
        ("TTS", TTS_OK),
        ("PDF", PDF_OK),
        ("Translate", TRANS_OK),
        ("Thinking", True),
        ("Streaming", True),
    ]
    badges = ""
    for name, ok in feats:
        cls = "active" if ok else "inactive"
        icon = "●" if ok else "○"
        badges += f'<span class="badge {cls}">{icon} {name}</span>'
    st.markdown(badges, unsafe_allow_html=True)

# ── Main chat ─────────────────────────────────────────────────────────────────
st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center;padding:60px 20px;opacity:.5;">
      <div style="font-size:3rem;margin-bottom:12px">⚡</div>
      <div style="font-family:'Space Mono',monospace;font-size:1.1rem;margin-bottom:6px">JARGONBOT INITIALIZED</div>
      <div style="font-size:.85rem">Gemma·3 · Thinking · 4-Word Answers · Multilingual</div>
    </div>
    """, unsafe_allow_html=True)

for i, msg in enumerate(st.session_state.messages):
    render_message(
        msg["role"],
        msg.get("answer", msg["content"]),
        msg.get("think", ""),
        i,
    )

st.markdown('</div>', unsafe_allow_html=True)

# ── Input area ────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

# Pre-fill from voice if available
voice_val = st.session_state.pop("voice_input", "")

col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_area(
        "Message",
        value=voice_val,
        placeholder="Ask anything… code, math, science, philosophy — JargonBot answers in 4 precise words.",
        height=80,
        label_visibility="collapsed",
        key="chat_input",
    )
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    send = st.button("⚡ SEND", use_container_width=True)

# quick prompts
qcols = st.columns(5)
quick = ["Explain quantum entanglement","Write Python quicksort","Summarize uploaded PDF",
         "Differential calculus basics","Machine learning overfitting"]
for i, q in enumerate(quick):
    if qcols[i].button(q[:20]+"…" if len(q)>20 else q, key=f"q{i}", use_container_width=True):
        user_input = q
        send = True

# ── Process ───────────────────────────────────────────────────────────────────
if send and user_input.strip():
    prompt = user_input.strip()

    # Translate input to English for model if needed
    if st.session_state.lang != "en" and TRANS_OK:
        prompt_en = GoogleTranslator(source="auto", target="en").translate(prompt)
    else:
        prompt_en = prompt

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt, "answer": prompt})
    st.session_state.msg_count += 1

    # Stream response
    thinking_placeholder = st.empty()
    answer_placeholder   = st.empty()

    full_text = ""
    with st.spinner(""):
        stream = stream_response(
            prompt_en,
            [m for m in st.session_state.messages[:-1]],
            st.session_state.pdf_context,
        )

        for delta, accumulated in stream:
            full_text = accumulated
            think_live, ans_live = extract_think_and_answer(full_text)

            # Show live thinking
            if think_live and st.session_state.thinking_visible:
                thinking_placeholder.markdown(f"""
                <div class="think-box">
                  <div class="think-title">⚡ PROCESSING…</div>
                  <div class="think-content">{think_live[-600:]}</div>
                </div>""", unsafe_allow_html=True)

            if ans_live:
                answer_placeholder.markdown(f"""
                <div style="font-family:'Space Mono',monospace;font-size:1.1rem;
                  color:#e2e8f0;font-weight:700;padding:8px 0;">
                  {ans_live}
                </div>""", unsafe_allow_html=True)

    # Clear live placeholders
    thinking_placeholder.empty()
    answer_placeholder.empty()

    # Final parse
    think_final, answer_final = extract_think_and_answer(full_text)

    # Translate answer if needed
    if st.session_state.lang != "en":
        answer_final = translate_text(answer_final, st.session_state.lang)

    # Store
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_text,
        "think":  think_final,
        "answer": answer_final,
    })
    st.session_state.last_think    = think_final
    st.session_state.last_response = answer_final
    st.session_state.msg_count += 1

    # TTS
    if st.session_state.voice_enabled and answer_final:
        speak_text(answer_final)

    st.rerun()