# archivo: app.py
from flask import Flask, request, send_file, jsonify
import requests
import time
import os

app = Flask(__name__)

api_keys = [
    {"api_key": "TU_API_KEY", "voice_id": "TU_VOICE_ID"},
]

UPLOAD_FOLDER = 'audios'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/convert', methods=['POST'])
def convert_text_to_audio():
    data = request.json
    texto = data.get('texto', '')

    if not texto:
        return jsonify({"error": "No se envió texto"}), 400

    current_api = api_keys[0]
    headers = {"xi-api-key": current_api["api_key"]}
    payload = {
        "text": texto,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        },
        "model_id": "eleven_multilingual_v1"
    }
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{current_api['voice_id']}"
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        timestamp = int(time.time())
        filename = f"{UPLOAD_FOLDER}/audio_{timestamp}.mp3"
        with open(filename, "wb") as f:
            f.write(response.content)
        return send_file(filename, mimetype="audio/mpeg", as_attachment=False)
    else:
        return jsonify({"error": "Error al generar audio"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
