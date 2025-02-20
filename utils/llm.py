from langchain_ollama import OllamaLLM
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from src.database.firebase import db


def get_settings_firestore(doc_name: str):
    try:
        doc_ref = db.collection("settings").document(doc_name)
        doc = doc_ref.get()

        if not doc.exists:
            raise ValueError(f"Configuration informations {doc_name} not found in Firestore.")
        return doc.to_dict()
    
    except Exception as e:
        raise ValueError(str(e))


def chat_llm(question: str):
    settings = get_settings_firestore("models")
    va_llm = settings.get("llm_platform")
    va_model_llm = settings.get("llm_model")

    if va_llm == "ollama":
        ollama_config = get_settings_firestore("connection_ollama")
        ollama_base_url = ollama_config.get("api_baseurl")

        if not ollama_base_url:
            raise ValueError(f"Configuration informations {va_llm} not found in Firestore.")
        
        ollama = OllamaLLM(base_url=ollama_base_url, model=va_model_llm, verbose=True)
        result = ollama.invoke(question)
        return result
    
    elif va_llm == "openai":
        openai_config = get_settings_firestore("connection_openai")
        openai_base_url = openai_config.get("api_baseurl")
        openai_api_key = openai_config.get("api_key")

        if not openai_api_key:
            raise ValueError(f"Configuration informations {va_llm} not found in Firestore.")
        
        openai = ChatOpenAI(base_url=f"{openai_base_url}/v1", api_key=openai_api_key, model=va_model_llm, temperature=0, streaming=True)
        result = ""
        try:
            stream_response = openai.stream(question)
            for chunk in stream_response:
                token = chunk.content
                result += token
                print(token, end="", flush=True)
        except Exception as e:
            error = str(e)
            if "401" in error and "Incorrect API key" in error:
                raise ValueError("Incorrect API key provided. Please check your OpenAI API key.")
            else:
                raise e
        return result

    else:
        raise ValueError("LLM platform must be 'openai' or 'ollama'.")


def embedder():
    settings = get_settings_firestore("models")
    va_embedder = settings.get("embedding_platform")
    va_model_embedder = settings.get("embedding_model")

    MODEL_EMBEDDING = va_model_embedder

    if va_embedder == "ollama":
        ollama_config = get_settings_firestore("connection_ollama")
        ollama_base_url = ollama_config.get("api_baseurl")
        EMBEDDER = OllamaEmbeddings(base_url=ollama_base_url, model=MODEL_EMBEDDING, show_progress=True)
        return MODEL_EMBEDDING, EMBEDDER
    elif va_embedder == "openai":
        openai_config = get_settings_firestore("connection_openai")
        openai_base_url = openai_config.get("api_baseurl")
        openai_api_key = openai_config.get("api_key")
        EMBEDDER = OpenAIEmbeddings(base_url=f"{openai_base_url}/v1", api_key=openai_api_key, model=MODEL_EMBEDDING)
        return MODEL_EMBEDDING, EMBEDDER
    else:
        raise ValueError("Embedding platform must be 'openai' or 'ollama'.")