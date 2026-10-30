from flask import Flask, request, jsonify
import os
import base64
import google.generativeai as genai

app = Flask(__name__)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        messages = data.get('messages', [])
        files_data = data.get('files', []) # Lista de múltiplos ficheiros
        
        if not messages and not files_data:
            return jsonify({'reply': 'Por favor, envie uma mensagem válida.'}), 400

        gemini_history = []
        for m in messages[:-1]:
            role = 'user' if m['sender'] == 'user' else 'model'
            gemini_history.append({'role': role, 'parts': [m['text']]})

        current_message = messages[-1]['text'] if messages else "Analise estes anexos."

        model = genai.GenerativeModel('gemini-3.8-flash')
        chat_session = model.start_chat(history=gemini_history)

        content_parts = [current_message]
        for f in files_data:
            file_bytes = base64.b64decode(f['data'])
            content_parts.append({
                'mime_type': f['mime_type'],
                'data': file_bytes
            })

        response = chat_session.send_message(content_parts)

        return jsonify({'reply': response.text})
    except Exception as e:
        return jsonify({'reply': f'Erro no processamento: {str(e)}'}), 500

if __name__ == '__main__':
    app.run()
