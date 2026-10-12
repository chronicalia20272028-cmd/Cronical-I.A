import os
from flask import Flask, request, jsonify, send_from_directory
from google import genai

app = Flask(__name__, static_folder='.', static_url_path='')

# Inicializa o cliente no modo Vertex AI utilizando o ID do teu projeto do Google Cloud
try:
    client = genai.Client(
        vertexai=True,
        project="704276061622",
        location="us-central1"
    )
except Exception as e:
    print(f"Erro ao inicializar o cliente Vertex AI: {e}")
    client = None

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    if not client:
        return jsonify({"reply": "Erro: Cliente Vertex AI não inicializado."}), 500

    data = request.get_json() or {}
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"reply": "Por favor, escreve uma mensagem."}), 400
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_message,
        )
        reply = response.text if response and response.text else "A IA não retornou conteúdo."
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Erro ao processar com a IA: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
