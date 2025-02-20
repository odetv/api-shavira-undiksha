import streamlit as st
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import run_model


EXAMPLE_QUESTIONS = [
    "Apa saja fasilitas yang disediakan oleh kampus undiksha?",
    "Dimana lokasi kampus Undiksha? Katanya ada juga di Denpasar.",
    "Saya lupa password SSO, cara atasinya gimana?",
    "Saya ingin cek kelulusan pendaftaran di Undiksha.",
    "Bagaimana cara akses melihat Kartu Tanda Mahasiswa?"
]
INITIAL_MESSAGE = {"role": "assistant", "content": "Salam Harmoni🙏 Ada yang bisa saya bantu?", "raw_content": "Salam Harmoni🙏 Ada yang bisa saya bantu?", "images": []}


def setup_page():
    st.set_page_config(page_title="Shavira Undiksha", layout="wide", page_icon="public/images/logo.png")
    st.sidebar.image("public/images/logo.png")
    st.sidebar.title("Virtual Assistant Shavira Undiksha")
    st.sidebar.write("Hai, selamat datang di Virtual Assistant Undiksha! Aku siap membantumu.")
    st.sidebar.markdown("""
    <p style="color:gray;">
        <small>Developed by: <strong>Gelgel & Sudiartika</strong></small><br>
        <small>Support by: <strong>UPA TIK Undiksha</strong></small>
    </p>
    """, unsafe_allow_html=True)
    st.title("Tanya Shavira😊")


def process_response(prompt):
    with st.spinner("Sedang memproses, harap tunggu..."):
        _, response = run_model(prompt)
        msg = re.sub(
            r'(https://aka\.undiksha\.ac\.id/api/ktm/generate/\S*)', 
            r'[Preview URL](\1)',
            response
        )
        html_msg = re.sub(
            r'(https://aka\.undiksha\.ac\.id/api/ktm/generate/\S*)', 
            r'<a href="\1" target="_blank">[Preview URL]</a>', 
            response
        )
        images = [
            link for link in re.findall(r'(https?://\S+)', msg)
            if "https://aka.undiksha.ac.id/api/ktm/generate" in link or link.endswith(('.jpg', '.jpeg', '.png', '.gif'))
        ]
        return {"msg": msg, "html_msg": html_msg, "images": images}


def add_message(role, content, html_content=None, images=None):
    if "messages" not in st.session_state:
        st.session_state.messages = [INITIAL_MESSAGE]
    message = {
        "role": role,
        "content": html_content if html_content else content,
        "raw_content": content,
        "images": images or []
    }
    st.session_state.messages.append(message)


def display_example_questions():
    cols = st.columns(len(EXAMPLE_QUESTIONS))
    for col, prompt in zip(cols, EXAMPLE_QUESTIONS):
        with col:
            if st.button(prompt):
                add_message("user", prompt)
                st.session_state['user_question'] = prompt
                response = process_response(prompt)
                add_message("assistant", response["msg"], response["html_msg"], response["images"])
                st.rerun()


def display_chat_history():
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["raw_content"])
        for img_url in msg.get("images", []):
            st.image(img_url)


def handle_user_input():
    if prompt := st.chat_input("Ketik pertanyaan Anda di sini..."):
        add_message("user", prompt)
        st.session_state['user_question'] = prompt
        st.chat_message("user").write(prompt)
        response = process_response(prompt)
        add_message("assistant", response["msg"], response["html_msg"], response["images"])
        st.chat_message("assistant").markdown(response["msg"])
        for img_url in response["images"]:
            st.image(img_url)


def main():
    setup_page()
    display_example_questions()
    st.markdown("***")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [INITIAL_MESSAGE]
    
    display_chat_history()
    handle_user_input()

if __name__ == "__main__":
    main()