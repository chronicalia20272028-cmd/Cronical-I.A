import os
from flask import Flask, request, jsonify, send_from_directory
from google import genai

app = Flask(__name__, static_folder='.', static_url_path='')

# Procura a chave de API em GEMINI_API_KEY ou GOOGLE_API_KEY
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

try:
    if api_key:
        client = genai.Client(api_key=api_key)
    else:
        client = genai.Client()
except Exception as e:
    print(f"Erro ao inicializar o cliente GenAI: {e}")
    client = None

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    if not client:
        return jsonify({"reply": "Erro: Cliente Gemini não inicializado. Verifica a chave de API nas variáveis do Render."}), 500

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
