from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from langchain_ollama import OllamaLLM


load_dotenv()
ollama_base_url = os.getenv('OLLAMA_BASE_URL')
openai_api_key = os.getenv('OPENAI_API_KEY')


def chat_ollama(question: str, model = "gemma2"):
    ollama = OllamaLLM(base_url=ollama_base_url, model=model, verbose=True)
    result = ollama.invoke(question)
    return result


def chat_openai(question: str):
    openai = ChatOpenAI(api_key=openai_api_key, model="gpt-4o-mini", temperature=0, streaming=True)
    result = ""
    stream_response = openai.stream(question)
    for chunk in stream_response:
        token = chunk.content
        result += token
        print(token, end="", flush=True)
    return result


def chat_groq(question: str):
    groq = ChatGroq(
        model="gemma2-9b-it",
        max_tokens=None,
        timeout=None,
    )
    result = groq.invoke(question).content if hasattr(groq.invoke(question), "content") else groq.invoke(question)
    return result

