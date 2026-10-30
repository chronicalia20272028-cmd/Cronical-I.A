from flask import Flask, request, jsonify
import os
import base64
import google.generativeai as genai

app = Flask(__name__)

# Configuração da chave de API do Gemini a partir das variáveis de ambiente da Vercel
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        messages = data.get('messages', [])
        image_data = data.get('image', None) # Recebe {mime_type, data} em base64 se houver anexo
        
        if not messages and not image_data:
            return jsonify({'reply': 'Por favor, envie uma mensagem válida.'}), 400

        # Montar o histórico de mensagens para a sessão de chat do Gemini
        gemini_history = []
        for m in messages[:-1]:
            role = 'user' if m['sender'] == 'user' else 'model'
            gemini_history.append({'role': role, 'parts': [m['text']]})

        current_message = messages[-1]['text'] if messages else "Analise esta imagem."

        # Modelo oficial Gemini 3.8-Flash otimizado e atualizado
        model = genai.GenerativeModel('gemini-3.8-flash')
        
        chat_session = model.start_chat(history=gemini_history)

        # Suporte a texto e imagens
        content_parts = [current_message]
        if image_data:
            image_bytes = base64.b64decode(image_data['data'])
            content_parts.append({
                'mime_type': image_data['mime_type'],
                'data': image_bytes
            })

        response = chat_session.send_message(content_parts)

        return jsonify({'reply': response.text})
    except Exception as e:
        return jsonify({'reply': f'Erro no processamento: {str(e)}'}), 500

if __name__ == '__main__':
    app.run()
