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
from langchain_core.messages import HumanMessage, SystemMessage
from configs.prompt import GENERAL_PROMPT


def general_chain(query: str):
    # 1. Load PDF Document
    loader = PyPDFDirectoryLoader("src/datasets/general")
    docs = loader.load()

    # Split dokumen
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,  #900
        chunk_overlap=100 #100
    )

    splits = text_splitter.split_documents(docs)

    print(splits)

    embeddings = OpenAIEmbeddings()
    if not os.path.exists("src/vectordb"):
        os.makedirs("src/vectordb")

    # Simpan ke FAISS
    if not os.path.exists("src/vectordb/db_general"):
        vectorstore = FAISS.from_documents(splits, embeddings)

        # Simpan vectorstore ke disk (opsional tapi direkomendasikan)
        vectorstore.save_local("src/vectordb/db_general")

    relevant_data = []

    # Cari dengan FAISS
    db = FAISS.load_local("src/vectordb/db_general", embeddings, allow_dangerous_deserialization=True)
    response = db.similarity_search_with_relevance_scores(query, k=10)
    for doc, similarity in response:
        relevant_data.append(doc.page_content)
        print(f"hasil Pencarian:")
        print(f"Content: {doc.page_content}")
        print(f"Similarity: {similarity}")
        print("-" * 50) 
    
    print("Relevan data", relevant_data)
    
    messages = f"""
        Pertanyaan pengguna: {query}
        Data yang diberikan: {relevant_data}
    """
    answer = chat_openai(messages, GENERAL_PROMPT)
    print("Isi prompt:\n", GENERAL_PROMPT)
    print("Hasil GENERAL CHAIN:\n", answer)
    return answer






