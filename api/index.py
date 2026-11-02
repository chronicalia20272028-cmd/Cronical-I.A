from flask import Flask, request, Response, jsonify
import os
import base64
import json
import google.generativeai as genai

app = Flask(__name__)

api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        if not api_key:
            return jsonify({'reply': 'Erro: GEMINI_API_KEY não configurada na Vercel.'}), 500

        data = request.get_json() or {}
        messages = data.get('messages', [])
        files_data = data.get('files', [])
        
        if not messages and not files_data:
            return jsonify({'reply': 'Envie uma mensagem válida.'}), 400

        gemini_history = []
        for m in messages[:-1]:
            role = 'user' if m.get('sender') == 'user' else 'model'
            text_content = m.get('text', '')
            if text_content:
                gemini_history.append({'role': role, 'parts': [text_content]})

        current_message = messages[-1].get('text', '') if messages else "Análise de anexos"

        model = genai.GenerativeModel('gemini-1.5-flash')
        chat_session = model.start_chat(history=gemini_history)

        content_parts = []
        if current_message:
            content_parts.append(current_message)

        for f in files_data:
            try:
                file_bytes = base64.b64decode(f['data'])
                content_parts.append({
                    'mime_type': f['mime_type'],
                    'data': file_bytes
                })
            except Exception:
                pass

        # Geração em tempo real (Stream)
        def generate():
            response_stream = chat_session.send_message(content_parts, stream=True)
            for chunk in response_stream:
                if chunk.text:
                    yield f"data: {json.dumps({'chunk': chunk.text})}\n\n"
            yield "data: [DONE]\n\n"

        return Response(generate(), mimetype='text/event-stream')

    except Exception as e:
        return jsonify({'reply': f'Erro no servidor: {str(e)}'}), 500

if __name__ == '__main__':
    app.run()
