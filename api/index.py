from flask import Flask, request, jsonify
import os
import google.generativeai as genai

app = Flask(__name__)

# Configura a chave da API do Gemini obtida nas variáveis de ambiente da Vercel
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'reply': 'Por favor, envie uma mensagem válida.'}), 400

        # Modelo atualizado conforme indicado pela API
        model = genai.GenerativeModel('gemini-3.8-flash')
        response = model.generate_content(user_message)

        return jsonify({'reply': response.text})
    except Exception as e:
        return jsonify({'reply': f'Erro no processamento: {str(e)}'}), 500

if __name__ == '__main__':
    app.run()
