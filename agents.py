from langgraph.graph import END, START, StateGraph
from typing import TypedDict, Literal, Optional
from langchain.memory import ConversationBufferMemory
from langchain_community.llms import Ollama
from openai import OpenAI
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from llm import chat_ollama, chat_openai
import os
import json

# Memuat file .env
load_dotenv()

base_url = os.getenv('BASE_URL')
openai_api_key = os.getenv('OPENAI_API')

class AgentState(TypedDict):
    context : str
    question_type : str
    question : str
    email: Optional[str] = None
    loginStatus : Optional[str] = None
    accountType : Optional[str] = None
    memory: ConversationBufferMemory
    incompleteReason : Optional[str] = None
    resetPasswordType : Optional[str] = None

def questionIdentifierAgent(state: AgentState):
    print("--- QUESTION IDENTIFIER AGENT ---")

    print(state['question'])
    prompt = """
        Anda adalah analis pertanyaan pengguna. Tugas anda adalah mengklasifikasikan pertanyaan yang masuk.
        Tergantung pada jawaban Anda, pertanyaan akan diarahkan ke tim yang tepat, jadi tugas Anda sangat penting.
        Ingat, Anda perlu memvalidasi pertanyaan harus pada konteks di Universitas Pendidikan Ganesha (Undiksha) saja.
        Perhatikan pertanyaan yang diberikan, harus cek pertanyaan agar spesifik lengkap sesuai konteks, jika tidak lengkap maka itu bisa jadi tidak sesuai konteks.
        Ada 6 kemungkinan pertanyaan yang diajukan:
        - ACCOUNT - Pertanyaan yang berkaitan dengan mengatur ulang password hanya pada akun email Universitas Pendidikan Ganesha (Undiksha) atau ketika user lupa dengan password email undiksha di gmail (google) atau user lupa password login di SSO E-Ganesha.
        - ACADEMIC - Pertanyaan yang berkaitan dengan informasi akademik (mata kuliah, jadwal kuliah, pembayaran Uang Kuliah Tunggal, dosen, program studi).
        - STUDENT - Pertanyaan berkaitan dengan informasi kemahasiswaan seperti organisasi kemahasiswaan, kegiatan kemahasiswaan, Unit Kegiatan Mahasiswa (UKM), Komunitas dan lain-lain.
        - NEWS - Pertanyaan yang berkaitan dengan berita-berita terkini di Universitas pendidikan Ganesha.
        - GENERAL - Pertanyaan yang menanyakan terkait dirimu yaitu SHAVIRA (Ganesha Virtual Assistant) dan
          menanyakan hal umum terkait Undiksha.
        - OUT OF CONTEXT - Jika tidak tahu jawabannya berdasarkan konteks yang diberikan.
        Hasilkan hanya satu kata (ACCOUNT, ACADEMIC, STUDENT, NEWS, GENERAL, OUT OF CONTEXT) berdasarkan pertanyaan yang diberikan.
    """

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=state['question']),
    ]

    response = chat_ollama(messages)

    return {"question_type": response}


def routeToSpecificAgent(state: AgentState): 
    return state['question_type']

def accountAgent(state: AgentState):
    print("\n--- ACCOUNT AGENT ---")

    prompt = f"""
        Pertanyaan : {state['question']}
        Dari pertanyaan diatas hasilkan JSON tanpa docstring, awalan, atau akhiran apapun, karena JSON tersebut akan dikonversi ke list.
        Berikut adalah key pada json tersebut:
        - "Email" : Email yang akan direset passwordnya, jika tidak disebutkan emailnya maka kembalikan string kosong (""),
        - "EmailType": Gunakan salah satu dari pilihan berikut sesuai dengan teks dari user : 
            - "GOOGLE EMAIL" (Ketika dari pernyataan user jelas menyebutkan "Akun Google", jika user hanya menyebutkan akun nya tanpa jelas memberikan pernyataan bahwa akan mereset akun GOOGLE maka alihkan ke INCOMPLETE INFORMATION), 
            - "SSO EMAIL" (ketika dari pernyataan user jelas menyebutkan reset password untuk SSO Undiksha atau E-Ganesha), 
            - "HYBRID EMAIL" (ketika dari pernyataan user jelas menyebutkan reset password untuk akun google undiksha dan SSO E-Ganesha), 
            - "INCOMPLETE INFORMATION" (ketika dari pernyataan user tidak jelas menyebutkan apakah reset password untuk akun google undiksha atau SSO E-Ganesha)
    """

    response = chat_openai(question=prompt, model='gpt-4o-mini')
    # response = chat_ollama(question=prompt, model='gemma2')

    print(response)

    try:
        result = json.loads(response)     
        email = result.get('Email')
        emailType = result.get('EmailType')
        

        if email and emailType: # Cek apakah email dan emailType ada atau tidak None
            reason = None
            if email.endswith("@undiksha.ac.id") or email.endswith("@student.undiksha.ac.id"):
                if emailType == 'SSO EMAIL':
                    return {"resetPasswordType": "SSO EMAIL"}
                elif emailType == 'GOOGLE EMAIL':
                    return {"resetPasswordType": "GOOGLE EMAIL"}
                elif emailType == 'HYBRID EMAIL':
                    return {"resetPasswordType": "HYBRID EMAIL"}
                else:
                    return {"resetPasswordType": "INCOMPLETE INFORMATION", "incompleteReason": reason} # INCOMPLETE INFORMATION
            else:
                reason = 'Email yang diinputkan bukan email undiksha, mohon gunakan email undiksha dengan domain @undiksha.ac.id atau @student.undiksha.ac.id'
                print(reason)
                return {"resetPasswordType": "INCOMPLETE INFORMATION", "incompleteReason": reason}
        elif email and not emailType:
            reason = 'user menyebtkan emailnya namun tidak menyebutkan apakah reset password untuk akun google undiksha atau SSO E-Ganesha'
            print(reason)
            return {"resetPasswordType": "INCOMPLETE INFORMATION", "incompleteReason": reason}
        elif not email and emailType:
            reason = 'Tidak disebutkan email yang ingin direset passwordnya'
            print(reason)
            return {"resetPasswordType": "INCOMPLETE INFORMATION", "incompleteReason": reason}
        else:
            reason = 'user tidak menyebutkan apakah reset password untuk akun google undiksha atau SSO E-Ganesha dan tidak menyebutkan email yang akan direset passwordnya'
            print(reason)
            return {"resetPasswordType": "INCOMPLETE INFORMATION", "incompleteReason": reason}

    except json.JSONDecodeError:
        # Handle the case where the response is not valid JSON
        "Ada yang salah bung"

def routeToSpecificEmailAgent(state: AgentState):
    return state['resetPasswordType']
    

def SSOEmailAgent(state: AgentState):
    print("--- SSO EMAIL AGENT ---")
    print('Baik sekarang kamu bisa cek di Email undiksha mu')
    pass

def GoogleEmailAgent(state: AgentState):
    print("--- GOOGLE EMAIL AGENT ---")
    pass

def HybridEmailAgent(state: AgentState):
    print("--- HYBRID EMAIL AGENT ---")
    pass

def incompleteInformationAgent(state: AgentState):
    print("\n--- INCOMPLETE INFORMATION AGENT ---")
    prompt = f"""
        Kamu adalah agen yang bertugas menjawab pertanyaan user yang hendak mereset password namun ada informasi yang kurang lengkap. Setiap menjawab pertanyaan selalu awalli dengan Salam Harmoni. Pertanyaan dari user adalah:  {state['question']}, sedangkan alasan tidak validnya karena : {state['incompleteReason']}
    Diakhir selalu selipkan kalimat seperti jika kebingungan terkait permasalahan tersebut bisa menghubungi UPA TIK (Unit Penunjang Akademik Teknologi Informasi dan Komunikasi) Undiksha. Buat agar jawaban yang kamu berikan nyambung dengan pertanyaan yang diberikan
    """

    response = chat_ollama(question=prompt, model='gemma2')

    print(response)


# ===============================================================================

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

def outOfContextAgent(state: AgentState):
    print("--- OUT OF CONTEXT AGENT ---")
    pass

# Definisikan Langgraph
workflow = StateGraph(AgentState)

# Definisikan Node
workflow.add_node('question_identifier', questionIdentifierAgent)
workflow.add_node('account', accountAgent)
workflow.add_node('academic', academicAgent)
workflow.add_node('student', studentAgent)
workflow.add_node('news', newsAgent)
workflow.add_node('general', generalAgent)
workflow.add_node('outOfContext', outOfContextAgent)
workflow.add_node('SSOEmailAgent', SSOEmailAgent)
workflow.add_node('GoogleEmailAgent', GoogleEmailAgent)
workflow.add_node('HybridEmailAgent', HybridEmailAgent)
workflow.add_node('incompleteInformationAgent', incompleteInformationAgent)

# Definisikan Edge

# AGEN KELAS 1
workflow.add_edge(START, 'question_identifier')
workflow.add_conditional_edges(
    'question_identifier',
    routeToSpecificAgent, {
        "ACCOUNT \n": 'account',
        "ACADEMIC \n": 'academic',
        "STUDENT \n": 'student',
        "NEWS \n": 'news',
        "GENERAL \n": 'general',
        "OUT OF CONTEXT \n": 'outOfContext',
    }
)
workflow.add_conditional_edges(
    'account',
    routeToSpecificEmailAgent, {
        "SSO EMAIL": 'SSOEmailAgent',
        "GOOGLE EMAIL": 'GoogleEmailAgent',
        "HYBRID EMAIL": 'HybridEmailAgent',
        "INCOMPLETE INFORMATION": 'incompleteInformationAgent',
    }
)

# AGEN KELAS 2
workflow.add_edge('academic', END)
workflow.add_edge('student', END)
workflow.add_edge('news', END)
workflow.add_edge('general', END)

# AGEN KELAS 3
workflow.add_edge('incompleteInformationAgent', END)

# Compile Graph
graph = workflow.compile()


question = 'saya ingin reset password dengan email google gelgel@undiksha.ac.id'
graph.invoke({'question': question})