import streamlit as st
from google import genai

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Chronical I.A",
    page_icon="🤖",
    layout="centered"
)

# Estilização visual limpa e minimalista (compatível com o teu gosto de design)
st.markdown("""
    <style>
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        line-height: 1.5;
    }
    .user-msg {
        background-color: #1f6feb;
        color: white;
        text-align: right;
    }
    .ai-msg {
        background-color: #161b22;
        color: #e6edf3;
        border: 1px solid rgba(255,255,255,0.08);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #8b949e;'>Chronical I.A</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e;'>Assistente virtual inteligente e universal</p>", unsafe_allow_html=True)

# Inicializar o histórico de conversação na sessão do Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibir mensagens anteriores no chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Caixa de input para o utilizador escrever
if prompt := st.chat_input("Escreve uma mensagem..."):
    # Adicionar mensagem do utilizador ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gerar resposta da IA em backend (seguro e sem CORS)
    with st.chat_message("assistant"):
        with st.spinner("A pensar..."):
            try:
                # Chave de API oficial integrada de forma segura no servidor Python
                client = genai.Client(api_key="AQ.Ab8RN6K9nVvNcnnjMh5fDNgZSkllNtk88oYbvVMTq0vDaIO2Kg")
                
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=prompt,
                )
                
                ai_reply = response.text
                st.markdown(ai_reply)
                
                # Guardar resposta no histórico
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                
            except Exception as e:
                error_msg = f"Ocorreu um erro ao comunicar com a IA: {str(e)}"
                st.error(error_msg)
