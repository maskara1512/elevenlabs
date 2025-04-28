from flask import Flask, request, send_file

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        texto = request.form.get("texto")
        if not texto:
            return "No se recibió texto", 400
        
        # Aquí deberías procesar el texto como lo hacías antes:
        # generar el MP3 usando tu código de ElevenLabs
        
        nombre_archivo_generado = procesar_texto_a_audio(texto)  # Lógica que debes adaptar
        return send_file(nombre_archivo_generado, as_attachment=True)

    return '''
    <h1>Servidor activo</h1>
    <p>Envía texto usando el formulario de tu página.</p>
    '''

