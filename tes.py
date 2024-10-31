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


loader = PyPDFDirectoryLoader("src/datasets/general")
docs = loader.load()

# Split dokumen
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=900, 
    chunk_overlap=100
)

splits = text_splitter.split_documents(docs)

embeddings = OpenAIEmbeddings()
if not os.path.exists("test_db"):
    os.makedirs("test_db")

# Simpan ke FAISS
if not os.path.exists("test_db/db_general"):
    vectorstore = FAISS.from_documents(splits, embeddings)

    # Simpan vectorstore ke disk (opsional tapi direkomendasikan)
    vectorstore.save_local("test_db/db_general")

# Cari dengan FAISS
db = FAISS.load_local("test_db/db_general", embeddings, allow_dangerous_deserialization=True)
response = db.similarity_search_with_relevance_scores("resika arthana", k=5)
for doc, similarity in response:
    print(f"Content: {doc.page_content}")
    print(f"Similarity: {similarity}")
    print("-" * 50) 
