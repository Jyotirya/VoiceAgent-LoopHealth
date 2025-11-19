import os
import uuid
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from ai_agent import get_ai_response
from voice_service import transcribe_audio, text_to_speech

app = Flask(__name__)
CORS(app)

TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)

# Add this route to handle the initial Greeting
@app.route('/greet', methods=['GET'])
def greet():
    """
    Returns the welcome audio message immediately.
    """
    welcome_text = "Hello, I am Loop AI. How can I assist you with your hospital search today?"
    
    # Create a unique filename
    file_id = str(uuid.uuid4())
    output_path = os.path.join(TEMP_DIR, f"welcome_{file_id}.mp3")
    
    try:
        # Use your existing TTS function (works with Google or ElevenLabs)
        if text_to_speech(welcome_text, output_path):
             return send_file(output_path, mimetype="audio/mpeg")
        else:
            return jsonify({"error": "TTS Failed"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chat-voice', methods=['POST'])
def chat_voice():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file"}), 400

    audio_file = request.files['audio']
    file_id = str(uuid.uuid4())
    input_path = os.path.join(TEMP_DIR, f"input_{file_id}.webm")
    output_path = os.path.join(TEMP_DIR, f"output_{file_id}.mp3")

    try:
        audio_file.save(input_path)
        
        # 1. STT
        user_text = transcribe_audio(input_path)
        if not user_text: return jsonify({"error": "Could not understand audio"}), 400
        print(f"🗣️ User: {user_text}")

        # 2. LLM
        ai_response = get_ai_response(user_text)
        print(f"🤖 AI: {ai_response}")

        # 3. TTS
        if text_to_speech(ai_response, output_path):
            return send_file(output_path, mimetype="audio/mpeg")
        else:
            return jsonify({"error": "TTS Failed"}), 500

    finally:
        if os.path.exists(input_path): os.remove(input_path)

@app.route('/')
def home():
    return "✅ Loop AI Backend is Running! Connect your Frontend now."

if __name__ == '__main__':
    app.run(debug=True, port=5000)

