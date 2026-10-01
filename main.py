from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import List, Optional
import os
import datetime
from google import genai
from google.genai import types
from PIL import Image
import io
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Chronical I.A. Core", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

def obter_data_hora() -> str:
    """Devolve a data e hora atuais do sistema."""
    agora = datetime.datetime.now()
    return f"A data e hora atuais são: {agora.strftime('%d/%m/%Y %H:%M:%S')}"

@app.get("/", response_class=HTMLResponse)
def servir_frontend():
    """Serve a interface gráfica diretamente na raiz do site."""
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Erro: index.html não encontrado no servidor.</h1>"

@app.post("/api/chat")
async def processar_chat(
    mensagem: str = Form(...),
    ficheiros: Optional[List[UploadFile]] = File(None)
):
    if not client:
        raise HTTPException(status_code=500, detail="Chave GEMINI_API_KEY não configurada no servidor.")
    
    try:
        conteudo_envio = [mensagem]
        
        if ficheiros:
            for f in ficheiros:
                dados = await f.read()
                if f.content_type and f.content_type.startswith('image'):
                    img = Image.open(io.BytesIO(dados))
                    conteudo_envio.append(img)
                else:
                    texto = dados.decode('utf-8', errors='ignore')
                    conteudo_envio.append(f"\n--- Ficheiro: {f.filename} ---\n{texto}")

        config_chat = types.GenerateContentConfig(
            tools=[obter_data_hora],
            temperature=0.7,
            system_instruction="Você é a Chronical I.A., um assistente de elite, altamente inteligente, direto e sofisticado."
        )

        chat_session = client.chats.create(model='gemini-2.0-flash', config=config_chat)
        resposta = chat_session.send_message(conteudo_envio)

        return {"status": "sucesso", "resposta": resposta.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))