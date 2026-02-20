import streamlit as st
import requests
import json

# -----------------------
# Configuration
# -----------------------

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:latest"

CHARACTER_PROMPTS = {
    "iron man": """
You are Iron Man (Tony Stark).
Witty, sarcastic, genius, confident.
Use clever humor and charismatic tone.
""",
    "naruto": """
You are Naruto Uzumaki.
Energetic, optimistic, loud, determined.
Talk about becoming Hokage!
""",
    "sherlock": """
You are Sherlock Holmes.
Highly analytical, logical, observant.
Speak intelligently and deduce things.
"""
}

# -----------------------
# Helper Functions
# -----------------------

def detect_character(text):
    text = text.lower()
    for character in CHARACTER_PROMPTS:
        if character in text:
            return character
    return None


def generate_response(prompt):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        if response.status_code == 200:
            return response.json()["response"]
        else:
            return "⚠️ Error: Could not get response from Gemma."

    except requests.exceptions.ConnectionError:
        return "⚠️ Ollama server not running. Start it using: ollama run gemma:3b"
    except Exception as e:
        return "⚠️ Unexpected error occurred."


def build_prompt(character_prompt, messages):
    conversation = ""
    for msg in messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        conversation += f"{role}: {msg['content']}\n"

    return f"""
{character_prompt}

Continue the conversation below while staying in character:

{conversation}
Assistant:
"""


# -----------------------
# Streamlit UI
# -----------------------

st.set_page_config(page_title="Gemma Character Chatbot", page_icon="🤖")

st.title("🎭 Gemma 3 Character Chatbot")
st.markdown("Mention a character like **Iron Man, Naruto, Sherlock** to switch personalities.")

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_character" not in st.session_state:
    st.session_state.current_character = None

# Chat input
user_input = st.chat_input("Type your message...")

if user_input:

    detected = detect_character(user_input)

    if detected:
        st.session_state.current_character = detected
        st.session_state.messages = []
        st.success(f"Switched to {detected.title()} mode 🎭")

    st.session_state.messages.append({"role": "user", "content": user_input})

    if st.session_state.current_character:
        char_prompt = CHARACTER_PROMPTS[st.session_state.current_character]
    else:
        char_prompt = "You are a helpful AI assistant."

    final_prompt = build_prompt(char_prompt, st.session_state.messages)

    response = generate_response(final_prompt)

    st.session_state.messages.append({"role": "assistant", "content": response})

# Display messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
