Here is your **updated GitHub README.md** with the **“Key Differences” section removed** and everything kept clean and professional.

You can directly replace your existing README with this.

---

# 🤖 Gemma AI Streamlit Suite

This repository contains **two AI chatbot interfaces powered by Ollama (Gemma 3)**:

1. ⚡ **JargonBot (Advanced AI UI)**
2. 🎭 **CharacterBot (Personality Chatbot)**

Both applications run locally using Ollama and Streamlit.

---

# 📁 Project Structure

```
├── jarvisui.py        # Advanced AI assistant (JargonBot)
├── characterbot.py    # Character-based chatbot
├── README.md
```

---

# ⚡ 1️⃣ JargonBot (jarvisui.py)

## 🧠 What It Does

JargonBot is a **highly customized AI assistant interface** built with Streamlit and Ollama.

It includes:

* 🔥 Real-time streaming responses
* 🧠 Visible AI thinking process
* 🌍 Multilingual support
* 📄 PDF document reader
* 🎤 Voice input (optional)
* 🔊 Text-to-speech (optional)
* 📊 Session statistics
* 🎨 Fully custom futuristic UI (custom CSS)
* 🧩 Model selector (any installed Ollama model)

---

## 🏗️ How It Works

* Uses Ollama local LLM (default: `gemma3:latest`)
* Injects a strict system prompt:

  * Shows reasoning inside `<think>` tags
  * Final answer formatted in a controlled structure
* Streams responses token-by-token
* Extracts `<think>` content and displays it separately
* Optionally reads uploaded PDFs and injects context
* Optional translation via Google Translator
* Optional voice recognition + TTS

---

## 🚀 Run JargonBot

```bash
streamlit run jarvisui.py
```

Make sure Ollama is running:

```bash
ollama serve
ollama pull gemma3
```

Optional dependencies:

```bash
pip install speechrecognition pyaudio pyttsx3 pymupdf deep-translator
```

---

# 🎭 2️⃣ CharacterBot (characterbot.py)

## 🧠 What It Does

CharacterBot is a **personality-switching chatbot**.

It detects character names in your message and dynamically switches the AI’s personality.

---

## 🎭 Available Characters

* **Iron Man** – Witty, sarcastic genius
* **Naruto** – Energetic, optimistic, determined
* **Sherlock** – Logical, analytical, observant

When a character name is mentioned, the system:

1. Switches to that character mode
2. Clears previous conversation
3. Continues the chat fully in-character

Example:

```
Talk like Iron Man
```

---

## 🏗️ How It Works

* Uses HTTP requests to Ollama REST API
* Builds conversation history manually
* Injects character-specific system prompt
* Sends prompt to Gemma model
* Displays response in Streamlit chat UI

---

## 🚀 Run CharacterBot

```bash
streamlit run characterbot.py
```

Ensure Ollama is running:

```bash
ollama serve
ollama pull gemma3
```

---

# 🛠️ Requirements

* Python 3.9+
* Streamlit
* Ollama installed locally
* Gemma model downloaded

Install core dependencies:

```bash
pip install streamlit requests ollama
```

---

# ⚙️ Ollama Setup

Install Ollama:

👉 [https://ollama.com](https://ollama.com)

Start server:

```bash
ollama serve
```

Download model:

```bash
ollama pull gemma3
```

---

# 💡 Future Improvements

* Add more character personalities
* Add streaming support to CharacterBot
* Deploy to cloud (AWS / GCP / Azure)
* Add authentication system
* Add persistent memory storage
* Convert into full backend API

---

# 📜 License

MIT License

---

# 👨‍💻 Author

Built as experimental AI interfaces powered by Ollama and Gemma 3.

---
# Chatbots
