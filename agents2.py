from langgraph.graph import END, START, StateGraph
from typing import TypedDict, Literal, Optional, Annotated, Sequence
from langchain.memory import ConversationBufferMemory
from utils.graph_image import get_graph_image
from utils.str_converter import str_to_list
from langchain_community.llms import Ollama
from openai import OpenAI
from operator import add
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from llm import chat_ollama, chat_openai
import os, re
import json

load_dotenv()

base_url = os.getenv('BASE_URL')
openai_api_key = os.getenv('OPENAI_API')

class AnswerState(TypedDict):
    agent = None
    answer = None

class AgentState(TypedDict):
    context = None
    question_type : Optional[str] = None
    question : str
    email: Optional[str] = None
    loginStatus : Optional[str] = None
    accountType : Optional[str] = None
    incompleteReason : Optional[str] = None
    resetPasswordType : Optional[str] = None
    agentAnswer : Annotated[Sequence[AnswerState], add]
    activeAgent : Optional[list] = None

def getResponseAndContext(question: str) -> str:
    prompt = """
        Anda adalah seoarang analis pertanyaan pengguna.
        Tugas Anda adalah mengklasifikasikan jenis pertanyaan pada konteks Undiksha (Universitas Pendidikan Ganesha).
        Tergantung pada jawaban Anda, akan mengarahkan ke agent yang tepat.
        Ada 6 konteks pertanyaan yang diajukan:
        - ACCOUNT - Pertanyaan yang berkaitan dengan mengatur ulang password hanya pada akun email Universitas Pendidikan Ganesha (Undiksha) atau ketika user lupa dengan password email undiksha di gmail (google) atau user lupa password login di SSO E-Ganesha.
        - ACADEMIC - Pertanyaan yang berkaitan dengan informasi akademik (mata kuliah, jadwal kuliah, pembayaran Uang Kuliah Tunggal, dosen, program studi).
        - STUDENT - Pertanyaan berkaitan dengan informasi kemahasiswaan seperti organisasi kemahasiswaan, kegiatan kemahasiswaan, Unit Kegiatan Mahasiswa (UKM), Komunitas dan lain-lain.
        - NEWS - Pertanyaan yang berkaitan dengan berita-berita terkini di Universitas pendidikan Ganesha.
        - GENERAL - Pertanyaan yang menanyakan terkait dirimu yaitu SHAVIRA (Ganesha Virtual Assistant) dan
          menanyakan hal umum terkait Undiksha.
        - OUT_OF_CONTEXT - Jika tidak tahu jawabannya berdasarkan konteks yang diberikan, serta tidak sesuai dengan 5 jenis pertanyaan diatas.
        Hasilkan hanya kata dari pilihan berikut (ACCOUNT, ACADEMIC, STUDENT, NEWS, GENERAL, OUT_OF_CONTEXT) berdasarkan pertanyaan yang diberikan, kemungkinan konteks pertanyaan lebih dari satu maka pisahkan dengan tanda koma.
    """

    messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=question),
        ]

    response = chat_ollama(messages)

    fixed_response = response.strip().lower()

    result = re.findall(r'\b\w+\b', fixed_response)

    return response, result


def questionIdentifierAgent(state: AgentState) :

    response, this_context = getResponseAndContext(state['question'])
    print(state["question"])
    print(this_context)

    print('--- QUESTION IDENTIFIER AGENT ---\n\n')
    return {"question_type": response, "activeAgent": this_context}

def accountAgent(state: AgentState):

    prompt = f"""
        Pertanyaan : {state['question']}
        anda adalah agen bertugas menjawab pertanyaan dengan spesifik
        - Apa email yang akan direset passwordnya, jika tidak disebutkan emailnya maka null,
        - Apa jenis email yang akan direset passwordnya, jawablah sesuai pilihan dibawah:
            - "GOOGLE_EMAIL" (ketika user menyebutkan jelas bahwa akan mereset akun google, jika user hanya menyebutkan akun nya tanpa jelas memberikan pernyataan bahwa akan mereset akun GOOGLE maka alihkan ke INCOMPLETE_INFORMATION), 
            - "SSO_EMAIL" (ketika dari pernyataan user jelas menyebutkan reset password untuk SSO Undiksha atau E-Ganesha), 
            - "HYBRID_EMAIL" (ketika dari pernyataan user jelas menyebutkan reset password untuk akun google undiksha dan SSO E-Ganesha),
            - "INCOMPLETE_INFORMATION" (ketika dari pernyataan user tidak menyebutkan apakah reset password untuk akun google undiksha atau SSO E-Ganesha)
        - Apa status login dari pertanyaan diatas, jawablah sesuai pilihan dibawah:
            - "TRUE" (Ketika user secara jelas bahwa akun undikshanya sudah diloginkan di perangkat baik hp/laptop/komputer),
            - "FALSE" (Ketika user secara jelas bahwa akun undikshanya belum diloginkan di perangkat baik hp/laptop/komputer)
            - "NO_INFO" (Ketika user tidak jelas apakah akun undikshanya sudah diloginkan di perangkat baik hp/laptop/komputer atau belum)
        jawab pertanyaan diatas, dengan jawaban dipisah dengan tanda koma, hasilkan hanya jawabannya saja
    """

    response = chat_openai(question=prompt, model='gpt-4o-mini')

    result = [item.strip() for item in response.split(",")]

    try:    
        email = result[0]
        emailType = result[1]
        loginStatus = result[2]
        print("email: ", email)
        print("emailType: ", emailType)
        print("loginStatus: ", loginStatus)
        validUndikshaEmail = email and (email.endswith("@undiksha.ac.id") or email.endswith("@student.undiksha.ac.id"))
        reason = None

        if "null" not in email: # Cek apakah email dan emailType bukan INCOMPLETE INFORMATION atau tidak None
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
                
        else:
            resetPasswordType = "INCOMPLETE_INFORMATION"
            reason = 'user tidak menyebutkan alamat email'
            
        print(f"Alasan incomplete: {reason}")
        print('--- ACCOUNT AGENT ---\n\n')
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
    print('--- STUDENT AGENT ---\n\n')

def newsAgent(state: AgentState):
    answer = "Informasi berita Undiksha"
    agent = "NEWS"
    print(f'--- {agent} AGENT ---\n\n')

    agentOpinion = {
        "agent": agent,
        "answer": answer
    }

    return {"agentAnswer": [agentOpinion]}

def generalAgent(state: AgentState):
    print("Informasi umum Undiksha.")
    print('--- GENERAL AGENT ---\n\n')

    answer = "Informasi umum Undiksha."
    agent = "GENERAL"

    agentOpinion = {
        "agent": agent,
        "answer": answer
    }

    return {"agentAnswer": [agentOpinion]}

def outOfContextAgent(state: AgentState):
    print('--- OUT OF CONTEXT AGENT ---')

def writterAgent(state: AgentState):
    if len(state["agentAnswer"]) == len(state["activeAgent"]):
        print("Ini agen yang aktif", state["activeAgent"])
        print("Ini jawaban dari agen yang aktif", state["agentAnswer"])

        prompt = f"""
            pertanyaan: {state["question"]}
            Urutan agen berdasarkan pertanyaan: {state["activeAgent"]}
            Jawaban dari tiap agen: {state["agentAnswer"]}


            adalah penulis yang bertugas menuliskan jawaban dari agen lain dari sudut pandang kamu sebagai chatbot, namun jangan sebutkan agennya  
            jawaban agennya sesuaikan dengan urutan agennya, berikan hanya jawabannya saja
        """

        response = chat_openai(question=prompt, model='gpt-4o-mini')

        print("\nRespose Dari SHAVIRA:\n", response)
        print('--- WRITTER AGENT ---')

def SSOEmailAgent(state: AgentState):
    print('--- SSO EMAIL AGENT ---')

def GoogleEmailAgent(state: AgentState):
    print('--- GOOGLE EMAIL AGENT ---')

def HybridEmailAgent(state: AgentState):
    print('--- HYBRID EMAIL AGENT ---')

def incompleteInformationAgent(state: AgentState):

    prompt = f"""
        Kamu adalah agen yang bertugas menjawab pertanyaan user yang hendak mereset password namun ada informasi yang kurang lengkap. Ikuti aturan ini:
        - jelaskan bahwa kamu hanya menerima akun Google atau SSO Undiksha (@undiksha.ac.id atau @student.undiksha.ac.id) dan tidak untuk akun google selain itu. 
        - Diakhir selalu selipkan kalimat seperti jika kebingungan terkait permasalahan tersebut bisa menghubungi UPA TIK (Unit Penunjang Akademik Teknologi Informasi dan Komunikasi) Undiksha. Buat agar jawaban yang kamu berikan nyambung dengan pertanyaan yang diberikan
        Pertanyaan dari user adalah:  {state['question']}, sedangkan alasan tidak validnya karena : {state['incompleteReason']}
    """

    response = chat_ollama(question=prompt, model='gemma2')

    agent = "ACCOUNT"

    agentOpinion = {
        "agent": agent,
        "answer": response
    }

    print('--- INCOMPLETE INFORMATION AGENT ---')
    return {"agentAnswer": [agentOpinion]}
    


def resetPasswordAgent(state: AgentState):
    print("-- RESET PASSWORD AGENT --")

def identityVerificatorAgent(state: AgentState):
    print("-- IDENTITY VERIFICATOR AGENT --")

def incompleteSSOStatment(state: AgentState):
    print("-- INCOMPLETE SSO STATEMENT --")

    agent = "ACCOUNT"
    answer = "Tanyakan apakah akun undiksha tersebut sudah diloginkan di perangkatnya?"
    agentOpinion = {
        "agent": agent,
        "answer": answer
    }

    return {"agentAnswer": [agentOpinion]}

def build_graph(question):
    workflow = StateGraph(AgentState)
    # level 1
    workflow.add_node("questionIdentifier", questionIdentifierAgent)
    workflow.add_node("writter", writterAgent)
    workflow.add_edge(START, "questionIdentifier")

    # Apakah workflow bisa dilempar ke fungsi lain???

    _, context = getResponseAndContext(question)

    if 'account' in context:
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



    if "academic" in context:
        workflow.add_node("academic", academicAgent)
        workflow.add_edge("questionIdentifier", "academic")
        workflow.add_edge("academic", "writter")

    if "student" in context:
        workflow.add_node("student", studentAgent)
        workflow.add_edge("questionIdentifier", "student")
        workflow.add_edge("student", "writter")

    if "news" in context:
        workflow.add_node("news", newsAgent)
        workflow.add_edge("questionIdentifier", "news")
        workflow.add_edge("news", "writter")

    if "general" in context:
        workflow.add_node("general", generalAgent)
        workflow.add_edge("questionIdentifier", "general")
        workflow.add_edge("general", "writter")

    if "out_of_context" in context :
        workflow.add_node("outOfContext", outOfContextAgent)
        workflow.add_edge("questionIdentifier", "outOfContext")
        workflow.add_edge("outOfContext", "writter")

    workflow.add_edge("writter", END)

    graph = workflow.compile()
    graph.invoke({'question': question})
    get_graph_image(graph)

build_graph("saya ingin restpassword akun pada akun sso undiksha asiapp@undiksha.ac.id dan saya sudah login diperangkat hp saya")






