# 🤖 Nyx — AI Voice Assistant

Nyx is a conversational voice assistant inspired by Friday (Iron Man). It listens to your voice, thinks with Google Gemini, and responds out loud using text-to-speech — all running locally on your machine.

---

## 🧠 How it works

```
🎙️ You speak → [RealtimeSTT] → text
text → [Gemini 2.5 Flash] → response
response → [pyttsx3] → 🔊 Nyx speaks
```

---

## ⚙️ Tech Stack

| Component | Library |
|---|---|
| Speech to Text | `RealtimeSTT` (Whisper tiny) |
| Language Model | `Google Gemini 2.5 Flash` |
| Text to Speech | `pyttsx3` (SAPI5 - local) |
| Env Security | `cryptography` (Fernet encryption) |

---

## 📁 Project Structure

```
ai_assistant/
├── main.py              # Main assistant loop
├── encrypt_env.py       # Script to encrypt your .env file
├── .env.encrypted       # Encrypted API keys (safe to commit)
├── .env.key             # ⚠️ NEVER commit this (store outside project)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🔐 Security — Encrypted API Keys

This project uses Fernet symmetric encryption to protect API keys. The `.env` file is encrypted into `.env.encrypted`, which is safe to push to GitHub. The key (`.env.key`) is stored outside the project folder.

**Files:**
- `.env.key` → The encryption key. Store in a safe place (e.g. Desktop). **Never commit this.**
- `.env.encrypted` → The encrypted secrets. Safe to commit.
- `.env` → Delete after encrypting.

**To encrypt your `.env`:**
```bash
python encrypt_env.py
```

---

## 🚀 Setup

### 1. Clone the repo
```bash
git clone https://github.com/Kapytanpirynola/ai_assistant.git
cd ai_assistant
```

### 2. Create and activate conda environment
```bash
conda create -n test python=3.13
conda activate test
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your API keys

Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

Then encrypt it:
```bash
python encrypt_env.py
```

Move `.env.key` to a safe location outside the project and delete the `.env` file.

### 5. Run
```bash
python main.py
```

---

## 💬 Usage

- Just speak — Nyx listens automatically
- Say `exit` to quit
- Nyx responds in Spanish by default

---

## 📦 Requirements

```
google-genai
python-dotenv
RealtimeSTT
torch
pyttsx3
cryptography
```

---

## ⚠️ .gitignore

Make sure your `.gitignore` includes:
```
.env
.env.key
__pycache__/
*.pyc
```

---

## 📌 Notes

- TTS uses Windows SAPI5 voices (Helena - Spanish by default)
- STT uses Whisper `tiny` model for low latency
- Gemini context is maintained across the full conversation session
