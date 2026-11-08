from flask import Flask, request, jsonify
import os
import base64
import google.generativeai as genai

app = Flask(__name__)

api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def get_gemini_model():
    # 1. Procura dinamicamente por qualquer modelo disponível que suporte geração de conteúdo
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return genai.GenerativeModel(m.name)
    except Exception as e:
        print("Aviso ao listar modelos:", e)

    # 2. Lista de fallback com os modelos mais estáveis
    fallbacks = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro', 'gemini-1.0-pro']
    for name in fallbacks:
        try:
            return genai.GenerativeModel(name)
        except Exception:
            continue
            
    # 3. Padrão final de segurança
    return genai.GenerativeModel('gemini-1.5-flash')

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

        # Obtém o modelo ativo automaticamente
        model = get_gemini_model()
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
        return jsonify({'reply': f'Erro no servidor ao processar o pedido: {str(e)}'}), 200

if __name__ == '__main__':
    app.run()
