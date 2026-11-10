from flask import Flask, request, jsonify
import os
import base64
import time
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
                gemini_history.append({'role': role, 'parts': [text_content]})

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

        # Tentativa com repetição automática (retry) em caso de limite 429
        max_retries = 3
        wait_time = 6
        response = None

        for attempt in range(max_retries):
            try:
                response = chat_session.send_message(content_parts)
                break
            except Exception as api_err:
                err_str = str(api_err)
                if ("429" in err_str or "quota" in err_str.lower()) and attempt < max_retries - 1:
                    time.sleep(wait_time)
                    wait_time *= 2  # Aumenta o tempo de espera progressivamente
                    continue
                else:
                    raise api_err

        ai_reply = response.text if response and response.text else "Sem resposta gerada."
        return jsonify({'reply': ai_reply})

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            return jsonify({'reply': '⚠️ O limite temporário de requisições foi atingido. O sistema tentará reenviar automaticamente na próxima mensagem. Aguarde alguns segundos.'}), 200
        return jsonify({'reply': f'Erro no servidor ao processar o pedido: {error_msg}'}), 200

if __name__ == '__main__':
    app.run()
