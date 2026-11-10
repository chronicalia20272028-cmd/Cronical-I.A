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
            return jsonify({'reply': 'Erro: GEMINI_API_KEY não configurada na Vercel.'}), 200

        data = request.get_json() or {}
        messages = data.get('messages', [])
        files_data = data.get('files', [])
        
        if not messages and not files_data:
            return jsonify({'reply': 'Envie uma mensagem válida.'}), 200

        gemini_history = []
        for m in messages[:-1]:
            role = 'user' if m.get('sender') == 'user' else 'model'
            text_content = m.get('text', '')
            if text_content:
                geminit_history_item = {'role': role, 'parts': [text_content]}
                gemini_history.append(geminit_history_item)

        current_message = messages[-1].get('text', '') if messages else "Análise de anexos"

        model = genai.GenerativeModel('gemini-3.8-flash')
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

        response = chat_session.send_message(content_parts)
        ai_reply = response.text if response and response.text else "Sem resposta gerada."

        return jsonify({'reply': ai_reply})

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            return jsonify({'reply': '⚠️ **Limite de requisições excedido:** O plano gratuito permite no máximo 5 pedidos por minuto. Aguarde cerca de 15 segundos e tente enviar a mensagem novamente.'}), 200
        return jsonify({'reply': f'Erro no servidor ao processar o pedido: {error_msg}'}), 200

if __name__ == '__main__':
    app.run()
