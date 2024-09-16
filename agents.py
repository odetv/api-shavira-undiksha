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

result = chat_llm("Halo")
print(result)
