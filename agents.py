from langgraph.graph import END, START, StateGraph
from typing import TypedDict, Literal, Optional
from langchain_community.llms import Ollama
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
import os

# Memuat file .env
load_dotenv()

base_url = os.getenv('BASE_URL')

class AgentState(TypedDict):
    context : str
    question_type : str
    question : str
    email: Optional[str] = None
    loginStatus : Optional[str] = None
    accountType : Optional[str] = None


def chat_llm(question: str, model = 'gemma2'):
    
    llm = Ollama(base_url=base_url, model=model, verbose=True)
    result = llm.invoke(question)

    return result


def questionIdentifierAgent(state: AgentState):
    prompt = f"""
        Kamu adalah analis pertanyaan pengguna. Tugas anda adalah mengklasifikasikan
        pertanyaan yang masuk.

        Tergantung pada jawaban Anda, pertanyaan akan diarahkan ke tim yang tepat, 
        jadi tugas Anda sangat penting bagi tim kami.

        Ada empat kemungkinan pertanyaan yang diajukan 
        - ACCOUNT - pertanyaan yang berkaitan dengan mengatur ulang password akun email Universitas Pendidikan Ganesha (Undiksha) atau ketika user lupa dengan password email undiksha di gmail (google) atau user lupa password login di SSO E-Ganesha
        - ACADEMIC - pertanyaan yang berkaitan dengan informasi akademik (mata kuliah, jadwal kuliah, pembayaran Uang Kuliah Tunggal, dosen, program studi)
        - STUDENT - pertanyaan berkaitan dengan informasi kemahasiswaan seperti organisasi kemahasiswaan, kegiatan kemahasiswaan, Unit Kegiatan Mahasiswa (UKM), Komunitas dan lain-lain
        - NEWS - pertanyaan yang berkaitan dengan berita-berita terkini di Universitas pendidikan Ganesha
        - GENERAL - pertanyaan yang menanyakan terkait dirimu yaitu SHAVIRA (Ganesha Virtual Assistant) atau menanyakan hal umum terkait Undiksha

        Hasilkan hanya satu kata (ACCOUNT, ACADEMIC, STUDENT, NEWS, GENERAL) berdasarkan pertanyaan yang diberikan.
    """

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=state['question']),
    ]

    response = chat_llm(messages)

    print(response)

    return {"question_type": response}


def routeAgent(state: AgentState):
    pass

def emailAgent(state: AgentState):
    pass

def identityVerificatorAgent(state: AgentState):
    pass

def resetPasswordAgent(state: AgentState):
    pass

def incompleteAttributeAgent(state: AgentState):
    pass

def academicAgent(state: AgentState):
    pass

def studentAgent(state: AgentState):
    pass

def newsAgent(state: AgentState):
    pass

# Definisikan Langgraph
workflow = StateGraph(AgentState)

workflow.add_node('question_identifier', questionIdentifierAgent)
# workflow.add_node('email', emailAgent)
# workflow.add_node('identity_verificator', identityVerificatorAgent)
# workflow.add_node('reset_password', resetPasswordAgent)
# workflow.add_node('incomplete_attribute', incompleteAttributeAgent)
# workflow.add_node('academic', academicAgent)
# workflow.add_node('student', studentAgent)
# workflow.add_node('news', newsAgent)

workflow.add_edge(START, 'question_identifier')

graph = workflow.compile()

graph.invoke({'question': 'bagaimana cara mereset password'})