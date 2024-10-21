from openai import OpenAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from langchain_ollama import OllamaLLM

# Memuat file .env
load_dotenv()
base_url = os.getenv('BASE_URL')
openai_api_key = os.getenv('OPENAI_API')


def chat_ollama(question: str, model = 'gemma2'):
    try:
        ollama = OllamaLLM(base_url=base_url, model=model, verbose=True)
        result = ollama.invoke(question)

        return result
    
    except:
        print("Ada masalah di server OLLAMA")

def chat_openai(question: str, model = 'gpt-3.5-turbo-0125'):
    try:
        gpt_openai = OpenAI(api_key=openai_api_key)
        result = gpt_openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": question}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        return result.choices[0].message.content 
    
    except:
        print("Ada masalah dengan GPT")

def chat_groq(question: str):
    groq = ChatGroq(
        model="gemma2-9b-it",
        max_tokens=None,
        timeout=None,
    )
    result = groq.invoke(question).content if hasattr(groq.invoke(question), "content") else groq.invoke(question)
    return result