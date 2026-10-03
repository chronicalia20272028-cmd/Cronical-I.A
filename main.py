import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from google import genai

# Configura o Flask para procurar o index.html na mesma pasta
app = Flask(__name__, template_folder='.', static_folder='.')
CORS(app)

# Inicializa o cliente da Google GenAI (lê a chave GEMINI_API_KEY do ambiente)
client = genai.Client()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'response': 'Por favor, envia uma mensagem válida.'}), 400

        # Envia a mensagem para o modelo Gemini gerar a resposta real
        response = client.models.generate_content(
            model='gemini-3.1-flash',
            contents=user_message,
        )
        
        ai_reply = response.text
        return jsonify({'response': ai_reply})
        
    except Exception as e:
        print(f"Erro ao comunicar com a API do Gemini: {e}")
        return jsonify({'response': 'Ocorreu um erro ao processar a tua mensagem.'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
