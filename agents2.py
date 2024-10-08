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
        - OUT OF CONTEXT - Jika tidak tahu jawabannya berdasarkan konteks yang diberikan, serta tidak sesuai dengan 5 jenis pertanyaan diatas.
        Hasilkan  (ACCOUNT, ACADEMIC, STUDENT, NEWS, GENERAL, OUT OF CONTEXT) berdasarkan pertanyaan yang diberikan.
    """

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=question),
    ]
    
    response = chat_ollama(messages)

    this_context = str_to_list(response)

    print(f"Context: {this_context}")

    return response, this_context


def questionIdentifierAgent(state: AgentState) :
    print('--- QUESTION IDENTIFIER AGENT ---')

    response, this_context = getResponseAndContext(state['question'])

    return {"question_type": response, "context": this_context}

def accountAgent(state: AgentState):
    print('--- ACCOUNT AGENT ---')

    prompt = f"""
        Pertanyaan : {state['question']}
        Hasilkan dalam bentuk dictionary murni tanpa pembungkus, awalan dan akhiran apapun.
        Berikut key pada JSON tersebut:
        - "Email" : Email yang akan direset passwordnya, jika tidak disebutkan emailnya maka null,
        - "EmailType": Gunakan salah satu dari pilihan berikut sesuai dengan teks dari user, yaitu:
            - "GOOGLE_EMAIL" (Ketika dari pernyataan user jelas menyebutkan "Akun Google", jika user hanya menyebutkan akun nya tanpa jelas memberikan pernyataan bahwa akan mereset akun GOOGLE maka alihkan ke INCOMPLETE INFORMATION), 
            - "SSO_EMAIL" (ketika dari pernyataan user jelas menyebutkan reset password untuk SSO Undiksha atau E-Ganesha), 
            - "HYBRID_EMAIL" (ketika dari pernyataan user jelas menyebutkan reset password untuk akun google undiksha dan SSO E-Ganesha), 
            - "INCOMPLETE_INFORMATION" (ketika dari pernyataan user tidak jelas menyebutkan apakah reset password untuk akun google undiksha atau SSO E-Ganesha)
        - "LoginStatus": Gunakan salah satu dari pilihan berikut sesuai dengan teks dari user, yaitu:
            - "TRUE" (Ketika user secara jelas bahwa akun undikshanya sudah diloginkan di perangkat baik hp/laptop/komputer),
            - "FALSE" (Ketika user secara jelas bahwa akun undikshanya belum diloginkan di perangkat baik hp/laptop/komputer)
            - "NO_INFO" (Ketika user tidak jelas apakah akun undikshanya sudah diloginkan di perangkat baik hp/laptop/komputer atau belum)
    """

    response = chat_openai(question=prompt, model='gpt-4o-mini')
    # response = chat_ollama(question=prompt, model='gemma2')

    print(response)

    try:
        result = json.loads(response)     
        email = result.get('Email')
        emailType = result.get('EmailType')
        loginStatus = result.get('LoginStatus')
        print("email: ", email)
        print("emailType: ", emailType)
        print("loginStatus: ", loginStatus)
        validUndikshaEmail = email and (email.endswith("@undiksha.ac.id") or email.endswith("@student.undiksha.ac.id"))
        reason = None

        if email: # Cek apakah email dan emailType bukan INCOMPLETE INFORMATION atau tidak None
            if validUndikshaEmail:
                if emailType == 'SSO_EMAIL':
                    resetPasswordType = "SSO_EMAIL"
                elif emailType == 'GOOGLE_EMAIL':
                    resetPasswordType = "GOOGLE_EMAIL"
                elif emailType == 'HYBRID_EMAIL':
                    resetPasswordType = "HYBRID_EMAIL"
                else:
                    resetPasswordType = "INCOMPLETE_INFORMATION"
                    reason = "Tidak disebutkan apakah user ingin reset password Akun google Undiksha atau SSO E-Ganesha"
            else:
                resetPasswordType = "INCOMPLETE_INFORMATION"
                reason = 'Email yang diinputkan bukan email undiksha, mohon gunakan email undiksha dengan domain @undiksha.ac.id atau @student.undiksha.ac.id'
                print(reason)
        else:
            resetPasswordType = "INCOMPLETE_INFORMATION"
            reason = 'user tidak menyebutkan alamat email'
            print(reason)
            return {"resetPasswordType": "INCOMPLETE_INFORMATION", "incompleteReason": reason}
        
        return {"resetPasswordType": resetPasswordType, "incompleteReason": reason, "loginStatus": loginStatus}

    except json.JSONDecodeError as e:
        # Handle the case where the response is not valid JSON
        print(f"Err: {e}")

def routeToSpecificEmailAgent(state: AgentState):
    return state['resetPasswordType']

def checkEmailWaslogged(state: AgentState):
    return state['loginStatus']

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

def SSOEmailAgent(state: AgentState):
    print('--- SSO EMAIL AGENT ---')

def GoogleEmailAgent(state: AgentState):
    print('--- GOOGLE EMAIL AGENT ---')

def HybridEmailAgent(state: AgentState):
    print('--- HYBRID EMAIL AGENT ---')

def incompleteInformationAgent(state: AgentState):
    print('--- INCOMPLETE INFORMATION AGENT ---')

def resetPasswordAgent(state: AgentState):
    print("-- RESET PASSWORD AGENT --")

def identityVerificatorAgent(state: AgentState):
    print("-- IDENTITY VERIFICATOR AGENT --")

def incompleteSSOStatment(state: AgentState):
    print("-- INCOMPLETE SSO STATEMENT --")

def build_graph(question):
    workflow = StateGraph(AgentState)
    # level 1
    workflow.add_node("questionIdentifier", questionIdentifierAgent)
    workflow.add_node("writter", writterAgent)
    workflow.add_edge(START, "questionIdentifier")

    # Apakah workflow bisa dilempar ke fungsi lain???

    _, context = getResponseAndContext(question)

    if 'ACCOUNT' in context:
        # Level 2
        workflow.add_node("account", accountAgent)

        # level 3
        workflow.add_node("SSOEmail", SSOEmailAgent)
        workflow.add_node("UndikshaGoogleEmail", GoogleEmailAgent)
        workflow.add_node("HybridEmail", HybridEmailAgent)
        workflow.add_node("incompleteInformation", incompleteInformationAgent)

        # level 4
        workflow.add_node("resetPassword", resetPasswordAgent)
        workflow.add_node("identityVerificator", identityVerificatorAgent)
        workflow.add_node("incompleteSSOStatment", incompleteSSOStatment)


        # Define Edge
        workflow.add_edge("questionIdentifier", "account")
        workflow.add_edge("resetPassword", "writter")
        workflow.add_edge("identityVerificator", "writter")
        workflow.add_edge("incompleteSSOStatment", "writter")
        workflow.add_conditional_edges(
            "SSOEmail",
            checkEmailWaslogged, {
                "TRUE": "resetPassword",
                "FALSE": "identityVerificator",
                "NO_INFO" : "incompleteSSOStatment",
            }
        )

        workflow.add_edge("UndikshaGoogleEmail", "writter")
        workflow.add_edge("HybridEmail", "writter")
        workflow.add_edge("incompleteInformation", "writter")
        
        workflow.add_conditional_edges(
            'account',
            routeToSpecificEmailAgent, {
                'SSO_EMAIL': 'SSOEmail',
                'GOOGLE_EMAIL': 'UndikshaGoogleEmail',
                'HYBRID_EMAIL': 'HybridEmail',
                'INCOMPLETE_INFORMATION': 'incompleteInformation',
            }
        )



    if "ACADEMIC" in context:
        workflow.add_node("academic", academicAgent)
        workflow.add_edge("questionIdentifier", "academic")
        workflow.add_edge("academic", "writter")

    if "STUDENT" in context:
        workflow.add_node("student", studentAgent)
        workflow.add_edge("questionIdentifier", "student")
        workflow.add_edge("student", "writter")

    if "NEWS" in context:
        workflow.add_node("news", newsAgent)
        workflow.add_edge("questionIdentifier", "news")
        workflow.add_edge("news", "writter")

    if "GENERAL" in context:
        workflow.add_node("general", generalAgent)
        workflow.add_edge("questionIdentifier", "general")
        workflow.add_edge("general", "writter")

    if "OUT OF CONTEXT" in context :
        workflow.add_node("outOfContext", outOfContextAgent)
        workflow.add_edge("questionIdentifier", "outOfContext")
        workflow.add_edge("outOfContext", "writter")

    workflow.add_edge("writter", END)

    graph = workflow.compile()
    graph.invoke({'question': question})
    get_graph_image(graph)

build_graph("siapa rektor undiksha, reset akun sso saya")






