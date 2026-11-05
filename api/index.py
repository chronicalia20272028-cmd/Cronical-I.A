from flask import Flask, request, jsonify
import os
import base64
import google.generativeai as genai

app = Flask(__name__)

api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def get_working_model():
    """Busca dinamicamente um modelo compatível com a API key"""
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Ordem de preferência de modelos rápidos
        preferences = [
            'models/gemini-1.5-flash',
            'models/gemini-1.5-flash-latest',
            'models/gemini-2.0-flash',
            'models/gemini-1.5-pro',
            'models/gemini-pro'
        ]
        
        for pref in preferences:
            if pref in models:
                return pref
        
        # Se nenhum da lista preferencial for encontrado, usa o primeiro modelo disponível
        if models:
            return models[0]
    except Exception as e:
        print("Erro ao listar modelos:", e)
    
    return 'gemini-1.5-flash'

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

        # Seleciona o modelo correto de forma dinâmica
        chosen_model_name = get_working_model()
        model = genai.GenerativeModel(chosen_model_name)

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
        return jsonify({'reply': f'Erro no servidor: {str(e)}'}), 500

if __name__ == '__main__':
    app.run()
