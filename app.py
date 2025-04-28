from flask import Flask, request, send_file
import requests
import time
import os

app = Flask(__name__)

# Lista de tus API Keys con voz asociada (VERIFICA los voice_ids)
api_keys = [
    {"api_key": "sk_f7e70a5d4a534324ecc66f3c1998c8c95522331007aaf9c0", "voice_id": "s2vO3jXi1cjEZA8DGruX"},
    {"api_key": "sk_aa23ac8a750c5d201d07bd779409b9d05f460e49ecd7cef2", "voice_id": "dhRX7qIYSJMt3RPvg03o"},
    {"api_key": "sk_431772f6556b5ec8f682a4192f7b84cf5db8ae33c256df08", "voice_id": "eGZ4RxgNNxvLudtkF7vu"},
    {"api_key": "sk_782a421b5bec3a2a6ab181768089e80b7a73e9bf30deb6fd", "voice_id": "xsxiaLW1KecyRwy77YyZ"},
    {"api_key": "sk_72bd210cb068e8176c6986af0a72dedf5ba0a442f7e3289a", "voice_id": "7zkmJWg3UNiyz5mpqkoi"},
    {"api_key": "sk_9464916a4b4e6c200fdd7e1866194416d8dc38df928090a3", "voice_id": "ztkCAW8ji4z0jnTlHVq3"},
    {"api_key": "sk_e887e127382bc801679fed05cd8d96c0b0427a7277428650", "voice_id": "DNms8nFNPfSQPFJtm6T3"},
    {"api_key": "sk_bf1f8c5ecb3277d74d3e558c4cd6aeec2abb44c1b673808d", "voice_id": "NxSNlIsdNKEYkCNyINyZ"}
]

# Función para dividir el texto en fragmentos si es largo
def dividir_texto(texto, limite=2048):
    if len(texto) <= limite:
        return [texto.strip()]
    
    fragments = []
    start = 0
    while start < len(texto):
        end = start + limite
        punto_final = texto.rfind('.', start, end)
        punto_interrogacion = texto.rfind('?', start, end)
        punto_exclamacion = texto.rfind('!', start, end)
        
        indices_puntuacion = [punto_final, punto_interrogacion, punto_exclamacion]
        max_index = max([i for i in indices_puntuacion if i != -1 and i > start], default=end)
        
        if max_index == end:
            espacio = texto.rfind(' ', start, end)
            if espacio == -1:
                max_index = end
            else:
                max_index = espacio
        
        fragment = texto[start:max_index+1].strip()
        fragments.append(fragment)
        start = max_index + 1
    
    return fragments

# Función para procesar el texto con ElevenLabs y generar el audio
def procesar_texto_a_audio(texto):
    fragmentos = dividir_texto(texto, limite=2048)
    audios = []
    index_api_key = 0  # Comienza con la primera API Key

    for i, fragmento in enumerate(fragmentos):
        processed = False
        current_key_index = index_api_key
        
        while not processed and current_key_index < len(api_keys):
            current_api = api_keys[current_key_index]
            headers = {"xi-api-key": current_api["api_key"]}
            payload = {
                "text": fragmento,
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
                "model_id": "eleven_multilingual_v1"
            }
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{current_api['voice_id']}"
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                timestamp = int(time.time())
                nombre_archivo = f"salida_{timestamp}_{i+1}.mp3"
                with open(nombre_archivo, "wb") as f:
                    f.write(response.content)
                audios.append(nombre_archivo)
                processed = True
                index_api_key = (index_api_key + 1) % len(api_keys)
                break
            else:
                current_key_index += 1
        
        if not processed:
            return None  # Si no se pudo procesar con ninguna API key

    # Combina audios si hay varios fragmentos
    if len(fragmentos) > 1:
        from pydub import AudioSegment
        combined = AudioSegment.empty()
        for audio in audios:
            sound = AudioSegment.from_mp3(audio)
            combined += sound
        timestamp = int(time.time())
        nombre_final = f"salida_completa_{timestamp}.mp3"
        combined.export(nombre_final, format="mp3")
        
        # Elimina los fragmentos temporales
        for audio in audios:
            os.remove(audio)
        return nombre_final
    
    return audios[0]  # Si solo hay un fragmento

# Ruta que maneja el formulario (POST)
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        texto = request.form.get("texto")
        if not texto:
            return "No se recibió texto", 400
        
        nombre_archivo_generado = procesar_texto_a_audio(texto)
        if not nombre_archivo_generado:
            return "Error al generar la voz", 500
        
        return send_file(nombre_archivo_generado, as_attachment=True)

    return '''
    <h1>Servidor activo</h1>
    <p>Envía texto usando el formulario de tu página.</p>
    '''
    
if __name__ == "__main__":
    app.run(debug=True)


