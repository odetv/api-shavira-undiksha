import os
from langchain import hub
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, PyPDFDirectoryLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm import chat_groq, chat_openai
from config.prompt import GENERAL_AGENT_PROMPT

def general_chain(query: str):
    # 1. Load PDF Document
    loader = PyPDFDirectoryLoader("assets/datasets/GENERAL")
    docs = loader.load()

    # Split dokumen
    text_splitter = RecursiveCharacterTextSplitter(
        separators=[" "],
        chunk_size=900, 
        chunk_overlap=500
    )
    splits = text_splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings()
    if not os.path.exists("database"):
        os.makedirs("database")

    # Simpan ke FAISS
    if not os.path.exists("database/faiss_db"):
        vectorstore = FAISS.from_documents(splits, embeddings)

        # Simpan vectorstore ke disk (opsional tapi direkomendasikan)
        vectorstore.save_local("database/faiss_db")

    # Cari dengan FAISS
    db = FAISS.load_local("database/faiss_db", embeddings, allow_dangerous_deserialization=True)
    response = db.similarity_search_with_relevance_scores(query, k=5)
    # for doc, similarity in response:
    #     print(f"Content: {doc.page_content}")
    #     print(f"Similarity: {similarity}")
    #     print("-" * 50) 

    prompt = GENERAL_AGENT_PROMPT.format(question=query, data=response)
    answer = chat_openai(prompt, system_prompt="kamu adalah penulis", model='gpt-4o-mini')
    print("Isi prompt:\n", prompt)
    print("Hasil post retrieval:\n", answer)
    return answer






