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
from configs.prompt import ACADEMIC_PROMPT


def academic_chain(query: str):
    # 1. Load PDF Document
    loader = PyPDFDirectoryLoader("src/datasets/academic")
    docs = loader.load()

    # Split dokumen
    text_splitter = RecursiveCharacterTextSplitter(
        separators=[" "],
        chunk_size=900, 
        chunk_overlap=100
    )
    splits = text_splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings()
    if not os.path.exists("src/vectordb"):
        os.makedirs("src/vectordb")

    # Simpan ke FAISS
    if not os.path.exists("src/vectordb/db_academic"):
        vectorstore = FAISS.from_documents(splits, embeddings)

        # Simpan vectorstore ke disk (opsional tapi direkomendasikan)
        vectorstore.save_local("src/vectordb/db_academic")

    # Cari dengan FAISS
    db = FAISS.load_local("src/vectordb/db_academic", embeddings, allow_dangerous_deserialization=True)
    response = db.similarity_search_with_relevance_scores(query, k=5)
    # for doc, similarity in response:
    #     print(f"Content: {doc.page_content}")
    #     print(f"Similarity: {similarity}")
    #     print("-" * 50) 

    prompt = ACADEMIC_PROMPT.format(question=query, data=response)
    messages = [
        HumanMessage(prompt)
    ]
    answer = chat_openai(messages)
    print("Isi prompt:\n", prompt)
    print("Hasil post retrieval:\n", answer)
    return answer






