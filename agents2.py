from langgraph.graph import END, START, StateGraph
from typing import TypedDict, Literal, Optional
from langchain.memory import ConversationBufferMemory
from utils.graph_image import get_graph_image
from utils.str_converter import str_to_list
from langchain_community.llms import Ollama
from openai import OpenAI
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from llm import chat_ollama, chat_openai
import os
import json

load_dotenv()

base_url = os.getenv('BASE_URL')
openai_api_key = os.getenv('OPENAI_API')
context = ""

class AgentState(TypedDict):
    context = None
    question_type : Optional[str] = None
    question : str
    email: Optional[str] = None
    loginStatus : Optional[str] = None
    accountType : Optional[str] = None
    incompleteReason : Optional[str] = None
    resetPasswordType : Optional[str] = None


def getResponseAndContext(question: str) -> str:
    prompt = """
        Anda adalah analis pertanyaan pengguna. Tugas anda adalah mengklasifikasikan pertanyaan yang masuk.
        Tergantung pada jawaban Anda, pertanyaan akan diarahkan ke tim yang tepat, jadi tugas Anda sangat penting.
        Ingat, Anda perlu memvalidasi pertanyaan harus pada konteks di Universitas Pendidikan Ganesha (Undiksha) saja.
        jawaban HANYA dalam format list Python yang valid, contoh: ["CATEGORY1"] atau ["CATEGORY1", "CATEGORY2"].
        Perhatikan pertanyaan yang diberikan, harus cek pertanyaan agar spesifik lengkap sesuai konteks, jika tidak lengkap maka itu bisa jadi tidak sesuai konteks.
        Ada 6 kemungkinan pertanyaan yang diajukan:
        - ACCOUNT - Pertanyaan yang berkaitan dengan mengatur ulang password hanya pada akun email Universitas Pendidikan Ganesha (Undiksha) atau ketika user lupa dengan password email undiksha di gmail (google) atau user lupa password login di SSO E-Ganesha.
        - ACADEMIC - Pertanyaan yang berkaitan dengan informasi akademik (mata kuliah, jadwal kuliah, pembayaran Uang Kuliah Tunggal, dosen, program studi).
        - STUDENT - Pertanyaan berkaitan dengan informasi kemahasiswaan seperti organisasi kemahasiswaan, kegiatan kemahasiswaan, Unit Kegiatan Mahasiswa (UKM), Komunitas dan lain-lain.
        - NEWS - Pertanyaan yang berkaitan dengan berita-berita terkini di Universitas pendidikan Ganesha.
        - GENERAL - Pertanyaan yang menanyakan terkait dirimu yaitu SHAVIRA (Ganesha Virtual Assistant) dan
          menanyakan hal umum terkait Undiksha.
        - OUT OF CONTEXT - Jika tidak tahu jawabannya berdasarkan konteks yang diberikan.
        Hasilkan  (ACCOUNT, ACADEMIC, STUDENT, NEWS, GENERAL, OUT OF CONTEXT) berdasarkan pertanyaan yang diberikan.
    """

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=question),
    ]
    
    response = chat_ollama(messages)

    this_context = str_to_list(response)

    return response, this_context


def questionIdentifierAgent(state: AgentState) :
    print('--- QUESTION IDENTIFIER AGENT ---')

    response, this_context = getResponseAndContext(state['question'])

    return {"question_type": response, "context": this_context}

def accountAgent(state: AgentState):
    print('--- ACCOUNT AGENT ---')

def academicAgent(state: AgentState):
    print('--- ACADEMIC AGENT ---')

def studentAgent(state: AgentState):
    print('--- STUDENT AGENT ---')

def newsAgent(state: AgentState):
    print('--- NEWS AGENT ---')

def generalAgent(state: AgentState):
    print('--- GENERAL AGENT ---')

def outOfContextAgent(state: AgentState):
    print('--- OUT OF CONTEXT AGENT ---')

def writterAgent(state: AgentState):
    print('--- WRITTER AGENT ---')


def build_graph(question):
    builder = StateGraph(AgentState)
    builder.add_node("questionIdentifier", questionIdentifierAgent)
    builder.add_node("writter", writterAgent)
    builder.add_edge(START, "questionIdentifier")

    # Apakah builder bisa dilempar ke fungsi lain???

    _, context = getResponseAndContext(question)

    if 'ACCOUNT' in context:
        builder.add_node("account", accountAgent)
        builder.add_edge("questionIdentifier", "account")

    if "ACADEMIC" in context:
        builder.add_node("academic", academicAgent)
        builder.add_edge("questionIdentifier", "academic")
        builder.add_edge("academic", "writter")

    if "STUDENT" in context:
        builder.add_node("student", studentAgent)
        builder.add_edge("questionIdentifier", "student")
        builder.add_edge("student", "writter")

    if "NEWS" in context:
        builder.add_node("news", newsAgent)
        builder.add_edge("questionIdentifier", "news")
        builder.add_edge("news", "writter")

    if "GENERAL" in context:
        builder.add_node("general", generalAgent)
        builder.add_edge("questionIdentifier", "general")
        builder.add_edge("general", "writter")

    if "OUT OF CONTEXT" in context:
        builder.add_node("outOfContext", outOfContextAgent)
        builder.add_edge("questionIdentifier", "outOfContext")
        builder.add_edge("outOfContext", END)

    builder.add_edge("writter", END)

    graph = builder.compile()
    graph.invoke({'question': question})
    get_graph_image(graph)

build_graph("apa informasi akademik terkini dan berikan cara reset password atm")






