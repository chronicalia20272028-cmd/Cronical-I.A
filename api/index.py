from flask import Flask, request, jsonify
import os
import base64
import google.generativeai as genai

app = Flask(__name__)

api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        if not api_key:
            return jsonify({'reply': 'Erro: A variável GEMINI_API_KEY não está configurada no painel da Vercel.'}), 500

        data = request.get_json() or {}
        messages = data.get('messages', [])
        files_data = data.get('files', [])
        
        if not messages and not files_data:
            return jsonify({'reply': 'Por favor, envie uma mensagem válida.'}), 400

        gemini_history = []
        for m in messages[:-1]:
            role = 'user' if m.get('sender') == 'user' else 'model'
            text_content = m.get('text', '')
            if text_content:
                gemini_history.append({'role': role, 'parts': [text_content]})

        current_message = messages[-1].get('text', 'Analise estes anexos.') if messages else "Olá"

        model = genai.GenerativeModel('gemini-3.8-flash')
        chat_session = model.start_chat(history=gemini_history)

        content_parts = [current_message]
        for f in files_data:
            try:
                file_bytes = base64.b64decode(f['data'])
                content_parts.append({
                    'mime_type': f['mime_type'],
                    'data': file_bytes
                })
            except Exception:
                pass

        response = chat_session.send_message(content_parts)
        return jsonify({'reply': response.text})

    except Exception as e:
        return jsonify({'reply': f'Erro interno no servidor Python: {str(e)}'}), 500

if __name__ == '__main__':
    app.run()
