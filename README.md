# 🎙️ VoiceScribe — AI Speech-to-Text SaaS

![Python](https://img.shields.io/badge/Python-3.7%2B-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.2.5-black?style=flat-square&logo=flask)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

> **VoiceScribe** is a production-grade, SaaS-level speech recognition web application built with Flask. Upload audio files or record live from your microphone — transcribe in **27 languages** and export as **PDF or TXT**.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🌐 **27 Languages** | English, Spanish, French, Hindi, Japanese, Arabic, Chinese & more |
| ⚡ **Lightning Fast** | Powered by Google Speech API — results in under 5 seconds |
| 🎤 **Live Recording** | Record from microphone with real-time audio waveform visualizer |
| 📂 **Drag & Drop Upload** | Upload `.wav` `.mp3` `.flac` `.ogg` `.m4a` audio files |
| 📄 **PDF Export** | Beautifully formatted branded transcript PDF |
| 📝 **TXT Export** | Plain text transcript download |
| 🕓 **Transcript History** | Last 10 transcriptions saved in browser localStorage |
| 📋 **Copy & Share** | One-click copy or native Web Share API |
| 🔒 **Privacy First** | Audio is processed and immediately discarded |
| 💰 **Pricing Tiers** | Free / Pro / Enterprise plans (UI ready for payment integration) |

---

## 🛠️ Tech Stack

- **Backend:** Python · Flask · Flask-CORS
- **Speech:** `SpeechRecognition` (Google Speech API) · `pydub` · FFmpeg
- **Export:** `ReportLab` (PDF generation)
- **Frontend:** Vanilla HTML5 · CSS3 · JavaScript (no frameworks)
- **Design:** Glassmorphism · Inter font · Custom animations · IntersectionObserver

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/VEERAKARTHICK235/speech-recognition-system.git
cd speech-recognition-system
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg (required for audio conversion)

- **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- **macOS:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg`

### 4. Run the app

```bash
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

---

## 🚀 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Renders the main SaaS UI |
| `GET` | `/health` | Health check — returns `{"status": "ok", "version": "2.0.0"}` |
| `GET` | `/languages` | Returns all supported language codes and names |
| `POST` | `/upload` | Upload audio file for transcription (`file`, `lang`) |
| `POST` | `/record` | Submit recorded audio blob (`audio`, `lang`) |
| `POST` | `/download_pdf` | Generate and download transcript PDF (`text`) |
| `POST` | `/download_txt` | Generate and download transcript TXT (`text`) |

### Request Parameters

**`/upload` and `/record`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `file` / `audio` | File | ✅ | The audio file or blob |
| `lang` | String | ❌ | Language code (e.g. `en-US`, `hi-IN`). Defaults to `en-US` |

### Response Format

```json
{
  "text": "Hello, world!",
  "word_count": 2,
  "duration_seconds": 3.45
}
```

On error:
```json
{ "err": "Descriptive error message" }
```

---

## 📁 Project Structure

```
speech-recognition-system/
├── app.py                  # Flask backend (routes, transcription, exports)
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html          # Full SaaS frontend (single-page)
└── README.md
```

---

## 🔧 Environment & Deployment

### Local Development
```bash
python app.py
# Runs on http://127.0.0.1:5000 with debug=True
```

### Production (Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

---

## 📜 License

MIT © [VEERAKARTHICK235](https://github.com/VEERAKARTHICK235)
