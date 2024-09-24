import streamlit as st
from langchain_community.llms import Ollama

# Inisialisasi obrolan
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

st.title("Chat Interface seperti ChatGPT")

# Fungsi untuk chat dengan LLM

def chat_llm(question: str, model = 'gemma2'):
    llm = Ollama(base_url="http://119.252.174.189:11434", model=model, verbose=True)
    result = llm.invoke(question)

    return result

# Fungsi untuk menambah percakapan
def add_to_chat(user_input, bot_response):
    st.session_state.chat_history.append({"user": user_input, "bot": bot_response})

# Fungsi sederhana untuk menghasilkan balasan dari bot
def generate_response(user_input):
    # Ganti ini dengan fungsi bot sebenarnya atau integrasi ke model AI
    result = chat_llm(user_input)

    return result


prompt = f"""

    """

# Kotak input pengguna
user_input = st.text_input("Masukkan pesan:")

# Jika pengguna menekan Enter setelah mengetik pesan
if user_input:
    bot_response = generate_response(user_input)
    add_to_chat(user_input, bot_response)

# Menampilkan riwayat obrolan
if st.session_state.chat_history:
    for chat in st.session_state.chat_history:
        st.write(f"**Kamu:** {chat['user']}")
        st.write(f"**Bot:** {chat['bot']}")

# Reset chat
if st.button("Reset Chat"):
    st.session_state.chat_history = []
