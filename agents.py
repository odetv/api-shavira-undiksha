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
    prompt = """
        Kamu adalah analis pertanyaan pengguna. Tugas anda adalah mengklasifikasikan
        pertanyaan yang masuk.

        Tergantung pada jawaban Anda, pertanyaan akan diarahkan ke tim yang tepat, 
        jadi tugas Anda sangat penting bagi tim kami.

        Ada empat kemungkinan pertanyaan yang diajukan 
        - ACCOUNT - pertanyaan yang berkaitan dengan mengatur ulang password hanya pada akun email Universitas Pendidikan Ganesha (Undiksha) atau ketika user lupa dengan password email undiksha di gmail (google) atau user lupa password login di SSO E-Ganesha
        - ACADEMIC - pertanyaan yang berkaitan dengan informasi akademik (mata kuliah, jadwal kuliah, pembayaran Uang Kuliah Tunggal, dosen, program studi)
        - STUDENT - pertanyaan berkaitan dengan informasi kemahasiswaan seperti organisasi kemahasiswaan, kegiatan kemahasiswaan, Unit Kegiatan Mahasiswa (UKM), Komunitas dan lain-lain
        - NEWS - pertanyaan yang berkaitan dengan berita-berita terkini di Universitas pendidikan Ganesha
        - GENERAL - pertanyaan yang menanyakan terkait dirimu yaitu SHAVIRA (Ganesha Virtual Assistant) dan
          menanyakan hal umum terkait Undiksha

        Hasilkan hanya satu kata (ACCOUNT, ACADEMIC, STUDENT, NEWS, GENERAL) berdasarkan pertanyaan yang diberikan
    """

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=state['question']),
    ]

    response = chat_llm(messages)

    print("--- QUESTION IDENTIFIER AGENT ---")

    return {"question_type": response}


def routeToSpecificAgent(state: AgentState):
    return state['question_type']

def accountAgent(state: AgentState):
    print("--- ACCOUNT AGENT ---")
    pass

def academicAgent(state: AgentState):
    print("--- ACADEMIC AGENT ---")
    pass

def studentAgent(state: AgentState):
    print("--- STUDENT AGENT ---")
    pass

def newsAgent(state: AgentState):
    print("--- NEWS AGENT ---")
    pass

def generalAgent(state: AgentState):
    print("--- GENERAL AGENT ---")
    pass

# Definisikan Langgraph
workflow = StateGraph(AgentState)

workflow.add_node('question_identifier', questionIdentifierAgent)
workflow.add_node('account', accountAgent)
workflow.add_node('academic', academicAgent)
workflow.add_node('student', studentAgent)
workflow.add_node('news', newsAgent)
workflow.add_node('general', generalAgent)

workflow.add_edge(START, 'question_identifier')
workflow.add_conditional_edges(
    'question_identifier',
    routeToSpecificAgent, {
        "ACCOUNT \n": 'account',
        "ACADEMIC \n": 'academic',
        "STUDENT \n": 'student',
        "NEWS \n": 'news',
        "GENERAL \n": 'general',
    }
)

graph = workflow.compile()


question = 'bagaimana caranya mereset password'
print(question)
graph.invoke({'question': question})