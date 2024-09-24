from langgraph.graph import END, START, StateGraph
from typing import TypedDict, Literal, Optional
from langchain_community.llms import Ollama
from dotenv import load_dotenv
import os

# Memuat file .env
load_dotenv()

base_url = os.getenv('BASE_URL')

class AgentState(TypedDict):
    context : str
    question : str
    purpose : Optional[str] = None
    email: Optional[str] = None

def chat_llm(question: str, model = 'gemma2'):
    llm = Ollama(base_url=base_url, model=model, verbose=True)
    result = llm.invoke(question)

    return result

# # Definisikan Fungsi Agen 
""" 
1. Question Identifier Agent
Tugas : Menertukan tujuan dari pertanyaan user
""" 
def questionIdentifierAgent(state: AgentState):
    question = state['question']

    prompt = f"""
    Kamu adalah seorang analis pertanyaan user, tentukan pertanyaan user apakah ingin mereset password atau 
    hanya ingin bertanya-tanya terkait hal biasa. Jika user ingin mereset password, maka ketikkan 'reset password'. 
    jika user tidak ingin mereset password maka ketikan tujuan user.

    Ini pertanyaannya : {question} 
    """

    purpose = chat_llm(prompt)

    return {"question": question, "purpose": purpose}

def isWantToResetPassword(state: AgentState) -> Literal['reset password'] | Literal['retriever agent']:
    purpose = state['purpose']
    if 'reset password' in purpose:
        return "reset password"
    else:
        return "retriever agent"
        

"""
2. Reset Password Agent
Tugas : Mengatur ulang password user
"""
def canLoginToUndikshaEmail(state: AgentState):
    prompt = f"""
        Sekarang kamu adalah seorang penanya yang menanyakan apakah user sudah memasukkan email undiksha ke gmail.
        Jika sudah maka minta user untuk mengirimkan email undikshanya.
    """
 
# Retriever Agent
def retrieverAgent(state: AgentState):
    pass

# Writer Agent
def writerAgent(state: AgentState):
    pass

# Definisikan Langgraph
workflow = StateGraph(AgentState)

workflow.add_node('question_identifier', questionIdentifierAgent)
workflow.add_node('')

