from flask import Flask, request, jsonify
import os
import google.generativeai as genai

app = Flask(__name__)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        messages = data.get('messages', [])
        
        if not messages:
            return jsonify({'reply': 'Por favor, envie uma mensagem válida.'}), 400

        # Separa a mensagem atual e o histórico para dar memória à IA
        current_message = messages[-1].get('text', '')
        history_messages = messages[:-1]

        gemini_history = []
        for m in history_messages:
            role = 'user' if m['sender'] == 'user' else 'model'
            gemini_history.append({'role': role, 'parts': [m['text']]})

        model = genai.GenerativeModel('gemini-3.8-flash')
        chat_session = model.start_chat(history=gemini_history)
        response = chat_session.send_message(current_message)

        return jsonify({'reply': response.text})
    except Exception as e:
        return jsonify({'reply': f'Erro no processamento: {str(e)}'}), 500

if __name__ == '__main__':
    app.run()
