from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
# pyrefly: ignore [missing-import]
import speech_recognition as sr
# pyrefly: ignore [missing-import]
from pydub import AudioSegment
import os, tempfile, io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit

app = Flask(__name__)
CORS(app)

# ── Supported audio formats ──────────────────────────────────────────────────
ALLOWED_EXTENSIONS = {'.wav', '.mp3', '.flac', '.ogg', '.m4a', '.webm', '.ogg'}

# ── Language codes supported by Google Speech API ───────────────────────────
SUPPORTED_LANGUAGES = {
    'en-US': 'English (US)',
    'en-GB': 'English (UK)',
    'es-ES': 'Spanish',
    'fr-FR': 'French',
    'de-DE': 'German',
    'it-IT': 'Italian',
    'pt-BR': 'Portuguese (Brazil)',
    'ru-RU': 'Russian',
    'zh-CN': 'Chinese (Simplified)',
    'zh-TW': 'Chinese (Traditional)',
    'ja-JP': 'Japanese',
    'ko-KR': 'Korean',
    'ar-SA': 'Arabic',
    'hi-IN': 'Hindi',
    'tr-TR': 'Turkish',
    'nl-NL': 'Dutch',
    'pl-PL': 'Polish',
    'sv-SE': 'Swedish',
    'da-DK': 'Danish',
    'fi-FI': 'Finnish',
    'no-NO': 'Norwegian',
    'id-ID': 'Indonesian',
    'ms-MY': 'Malay',
    'th-TH': 'Thai',
    'vi-VN': 'Vietnamese',
    'ta-IN': 'Tamil',
    'te-IN': 'Telugu',
}


# ── Health check ─────────────────────────────────────────────────────────────
@app.route('/health')
def health():
    return jsonify(status='ok', version='2.0.0')


# ── Main page ─────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


# ── Language list endpoint ────────────────────────────────────────────────────
@app.route('/languages')
def languages():
    return jsonify(languages=SUPPORTED_LANGUAGES)


# ── Core transcription helper ─────────────────────────────────────────────────
def transcribe_file(file_stream, lang='en-US'):
    """
    Convert and transcribe an uploaded audio file.
    Returns a dict: { text, word_count, duration_seconds }
    """
    ext = os.path.splitext(file_stream.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported format '{ext}'. Accepted: "
            + ', '.join(sorted(ALLOWED_EXTENSIONS))
        )

    if lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language code '{lang}'.")

    # Convert to 16 kHz mono WAV for best recognition accuracy
    audio_seg = AudioSegment.from_file(file_stream)
    duration_seconds = round(len(audio_seg) / 1000, 2)

    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        (audio_seg
         .set_channels(1)
         .set_frame_rate(16000)
         .export(tmp.name, format='wav'))
        temp_path = tmp.name

    try:
        recog = sr.Recognizer()
        with sr.AudioFile(temp_path) as src:
            data = recog.record(src)
            text = recog.recognize_google(data, language=lang)
    except sr.UnknownValueError:
        raise ValueError("Speech could not be understood. Please check audio clarity.")
    except sr.RequestError as e:
        raise ConnectionError(f"Google Speech API unavailable: {e}")
    finally:
        os.unlink(temp_path)

    word_count = len(text.split()) if text else 0
    return {'text': text, 'word_count': word_count, 'duration_seconds': duration_seconds}


# ── Upload & transcribe ───────────────────────────────────────────────────────
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify(err="No audio file provided."), 400
    lang = request.form.get('lang', 'en-US')
    try:
        result = transcribe_file(request.files['file'], lang)
        return jsonify(**result)
    except ValueError as e:
        return jsonify(err=str(e)), 422
    except ConnectionError as e:
        return jsonify(err=str(e)), 503
    except Exception as e:
        return jsonify(err=f"Unexpected error: {e}"), 500


# ── Record & transcribe ───────────────────────────────────────────────────────
@app.route('/record', methods=['POST'])
def record():
    if 'audio' not in request.files:
        return jsonify(err="No audio data received."), 400
    lang = request.form.get('lang', 'en-US')
    audio_file = request.files['audio']
    # Browser sends webm/ogg — give it a recognizable name
    audio_file.filename = 'recording.webm'
    try:
        result = transcribe_file(audio_file, lang)
        return jsonify(**result)
    except ValueError as e:
        return jsonify(err=str(e)), 422
    except ConnectionError as e:
        return jsonify(err=str(e)), 503
    except Exception as e:
        return jsonify(err=f"Unexpected error: {e}"), 500


# ── PDF export ────────────────────────────────────────────────────────────────
@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    text = request.form.get('text', '').strip()
    if not text:
        return jsonify(err="No text to export."), 400

    buf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    c = canvas.Canvas(buf.name, pagesize=A4)
    width, height = A4
    margin = 60
    max_w = width - 2 * margin
    font_size = 12
    line_h = font_size * 1.5

    # Header
    c.setFont('Helvetica-Bold', 16)
    c.setFillColorRGB(0.42, 0.39, 1.0)
    c.drawString(margin, height - margin, 'VoiceScribe – Transcript')
    c.setStrokeColorRGB(0.42, 0.39, 1.0)
    c.setLineWidth(1.5)
    c.line(margin, height - margin - 8, width - margin, height - margin - 8)

    # Body
    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.setFont('Times-Roman', font_size)
    lines = []
    for para in text.split('\n'):
        wrapped = simpleSplit(para, 'Times-Roman', font_size, max_w)
        lines.extend(wrapped or [''])
        lines.append('')

    y = height - margin - 36
    for line in lines:
        if y < margin + 20:
            c.showPage()
            c.setFont('Times-Roman', font_size)
            c.setFillColorRGB(0.1, 0.1, 0.1)
            y = height - margin
        c.drawString(margin, y, line)
        y -= line_h

    c.save()
    return send_file(buf.name, as_attachment=True, download_name='voicescribe-transcript.pdf')


# ── TXT export ────────────────────────────────────────────────────────────────
@app.route('/download_txt', methods=['POST'])
def download_txt():
    text = request.form.get('text', '').strip()
    if not text:
        return jsonify(err="No text to export."), 400
    buf = io.BytesIO(text.encode('utf-8'))
    buf.seek(0)
    return send_file(
        buf,
        as_attachment=True,
        download_name='voicescribe-transcript.txt',
        mimetype='text/plain'
    )


if __name__ == '__main__':
    # use_reloader=False prevents Flask watchdog from scanning all of
    # site-packages and restarting the server on every pip-installed
    # package change.  Debugger and debug error pages remain active.
    app.run(debug=True, use_reloader=False)
