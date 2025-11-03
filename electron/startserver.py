import io, wave, base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from piper import PiperVoice
from converse import llm_response, transcribe, stream_speech

app = Flask(__name__)
CORS(app)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/listen_once")
def listen_once():
    """
    Triggers your Python-side mic capture -> STT -> LLM -> TTS.
    Audio is played by Piper on the Python side (not via Electron).
    """
    try:
        heard = transcribe()                 # uses your mic()
        reply = llm_response(heard)          # Ollama call
        stream_speech(reply)                 # Piper plays audio out speakers
        return jsonify({"heard": heard, "reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.post("/reply")
def reply_route():
    """
    Given text from Electron, get LLM reply and speak it with Piper.
    """
    data = request.get_json(force=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Missing 'text'"}), 400
    try:
        reply = llm_response(text)
        stream_speech(reply)
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.post("/say")
def say_route():
    """
    Directly speak text via Piper (no LLM).
    """
    data = request.get_json(force=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Missing 'text'"}), 400
    try:
        stream_speech(text)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Keep localhost-only by default
    app.run(host="127.0.0.1", port=8765, debug=False)