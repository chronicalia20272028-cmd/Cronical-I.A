import os
import time
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

        # Lista de modelos para tentar por ordem de prioridade caso algum esteja sobrecarregado
        models_to_try = ['gemini-1.5-flash', 'gemini-2.0-flash']
        ai_reply = None
        last_error = None

        # Tenta cada modelo com repetição em caso de falha temporária (503)
        for model_name in models_to_try:
            for attempt in range(2): # Tenta 2 vezes por modelo
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=user_message,
                    )
                    if response and response.text:
                        ai_reply = response.text
                        break
                except Exception as err:
                    last_error = err
                    time.sleep(1) # Aguarda 1 segundo antes de tentar novamente
            if ai_reply:
                break

        if ai_reply:
            return jsonify({'response': ai_reply})
        else:
            raise last_error or Exception("Todos os modelos falharam.")
        
    except Exception as e:
        print(f"Erro ao comunicar com a API do Gemini: {e}")
        return jsonify({'response': 'Os servidores da IA estão temporariamente sobrecarregados. Por favor, tenta enviar a mensagem novamente em instantes.'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
