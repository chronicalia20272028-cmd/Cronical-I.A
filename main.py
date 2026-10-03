import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai

app = Flask(__name__)
CORS(app)

# Inicializa o cliente da Google GenAI
# Garante que a chave GEMINI_API_KEY está configurada nas Environment Variables do Render
client = genai.Client()

@app.route('/')
def index():
    return "Chronical I.A Backend a funcionar!"

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'response': 'Por favor, envia uma mensagem válida.'}), 400

        # Envia a mensagem para o modelo Gemini gerar a resposta real
        response = client.models.generate_content(
            model='gemini-2.5-flash',
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
