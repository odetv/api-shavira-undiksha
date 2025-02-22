import os
import shutil
import requests
from zoneinfo import ZoneInfo
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, Depends, Request, UploadFile, File, Form
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_405_METHOD_NOT_ALLOWED
from typing_extensions import List
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings.ollama import OllamaEmbeddings
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from firebase_admin import firestore
from main import run_model
from src.config.config import DATASETS_DIR, VECTORDB_DIR
from api.initialize import app
from api.classes import QuestionRequest, DeleteDatasetsRequest, SetupConfigRequest, SetupQuickConfigRequest
from api.authentication import verify_bearer_token
from api.handler import (
    api_response,
    not_found_handler,
    method_not_allowed_handler,
    validation_exception_handler,
    http_exception_handler
)
from src.database.firebase import db


# Enpoint untuk base url root API request
@app.get("/", tags=["root"])
async def root(request_http: Request, token: str = Depends(verify_bearer_token)):
    timestamp = datetime.now(ZoneInfo("Asia/Makassar")).strftime("%Y-%m-%d %H:%M:%S")
    return JSONResponse(
        status_code=200,
        content={
            "statusCode": 200,
            "success": True,
            "message": "OK",
            "data": {
                "timestamp": timestamp,
                "description": "API Virtual Assistant Undiksha"
            }
        })


# Endpoint untuk melihat daftar file (List)
@app.get("/datasets/list", tags=["datasets"])
async def list_datasets(request_http: Request, token: str = Depends(verify_bearer_token)):
    if not os.path.exists(DATASETS_DIR):
        os.makedirs(DATASETS_DIR)
        raise HTTPException(status_code=404, detail="Datasets folder is created, but still empty.")
    
    datasets = [
        file for file in os.listdir(DATASETS_DIR)
        if file.lower().endswith(('.pdf', '.doc', '.docx'))
    ]
    if not datasets:
        raise HTTPException(status_code=404, detail="Datasets folder is empty or there are no PDF/Word files.")

    return api_response(
        request_http,
        status_code=200,
        success=True,
        message="Datasets found.",
        data=datasets
    )


# Endpoint untuk membaca konten file tertentu (Read)
@app.get("/datasets/read/{filename}", tags=["datasets"])
async def read_datasets(request_http: Request, filename: str):
    file_path = os.path.join(DATASETS_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    
    if filename.lower().endswith(".pdf"):
        def iter_file():
            with open(file_path, "rb") as file:
                yield from file
        return StreamingResponse(iter_file(), media_type="application/pdf", headers={"Content-Disposition": f"inline; filename={filename}"})
    elif filename.lower().endswith((".doc", ".docx")):
        return FileResponse(file_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={"Content-Disposition": f"attachment; filename={filename}"})
    else:
        raise HTTPException(status_code=400, detail="File format is not supported for display or download.")


# Endpoint untuk mengunggah file PDF/Word single atau multiple files (Create)
@app.post("/datasets/upload", tags=["datasets"])
async def upload_datasets(request_http: Request, files: List[UploadFile] = File(...), token: str = Depends(verify_bearer_token)):
    uploaded_files = []
    unsupported_files = []

    for file in files:
        if file.content_type not in ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            unsupported_files.append(file.filename)
            continue
        file_location = os.path.join(DATASETS_DIR, file.filename)
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)
        uploaded_files.append(file.filename)

    if not uploaded_files:
        raise HTTPException(status_code=400, detail="No file uploaded or the uploaded file is not supported.")
    if unsupported_files:
        return api_response(
            request_http,
            status_code=207,
            success=True,
            message="Some files are not supported.",
            data={"uploaded_files": uploaded_files, "unsupported_files": unsupported_files}
        )
    else:
        return api_response(
            request_http,
            status_code=201,
            success=True,
            message="Successfully uploaded all files.",
            data={"uploaded_files": uploaded_files}
        )


# Endpoint untuk memperbarui (Update) file
@app.put("/datasets/update", tags=["datasets"])
async def update_dataset(
    request_http: Request,
    target: str = Form(...),
    file: UploadFile = File(...),
    token: str = Depends(verify_bearer_token)
):
    old_filename = target
    new_filename = file.filename
    original_file_path = os.path.join(DATASETS_DIR, target)
    new_file_path = os.path.join(DATASETS_DIR, new_filename)

    if not os.path.isfile(original_file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    
    os.remove(original_file_path)
    with open(new_file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return api_response(
        request_http,
        status_code=200,
        success=True,
        message="Successfully updated the file.",
        data={
            "target": old_filename,
            "old_filename": old_filename,
            "new_filename": new_filename
        }
    )


# Endpoint untuk menghapus (Delete) file
@app.delete("/datasets/delete", tags=["datasets"])
async def delete_datasets(request_http: Request, request: DeleteDatasetsRequest, token: str = Depends(verify_bearer_token)):
    deleted_files = []
    not_found_files = []

    for filename in request.filenames:
        file_path = os.path.join(DATASETS_DIR, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
            deleted_files.append(filename)
        else:
            not_found_files.append(filename)

    if not_found_files:
        return api_response(
            request_http,
            status_code=207,
            success=True,
            message="Some files were not found.",
            data={"deleted_files": deleted_files, "not_found_files": not_found_files}
        )
    if not deleted_files:
        raise HTTPException(status_code=400, detail="No file was selected.")
    else:
        return api_response(
            request_http,
            status_code=200,
            success=True,
            message="Successfully deleted all files.",
            data={"deleted_files": deleted_files}
        )


async def get_llm(llm_platform: str):
    try:
        if llm_platform == "openai":
            doc_ref = db.collection("settings").document("connection_openai")
        elif llm_platform == "ollama":
            doc_ref = db.collection("settings").document("connection_ollama")
        else:
            raise HTTPException(status_code=400, detail=f"LLM platform {llm_platform} invalid.")

        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=500, detail=f"Configuration informations {llm_platform} not found in Firestore.")
        
        api_baseurl = doc.to_dict().get("api_baseurl")

        headers = {}
        if llm_platform == "openai":
            openai_api_key = doc.to_dict().get("api_key")
            if openai_api_key:
                headers["Authorization"] = f"Bearer {openai_api_key}"

        response = requests.get(f"{api_baseurl}/v1/models", headers=headers)
        response.raise_for_status()
        models = response.json()
        return [model["id"] for model in models.get("data", [])]
    
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")


def get_embedding(embedding_platform: str, embedding_model: str):
    try:
        if embedding_platform.lower() == "openai":
            doc_ref = db.collection("settings").document("connection_openai")
        elif embedding_platform.lower() == "ollama":
            doc_ref = db.collection("settings").document("connection_ollama")
        else:
            raise HTTPException(status_code=400, detail=f"Embedding platform {embedding_platform} invalid.")
        
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=500, detail=f"Configuration informations {embedding_platform} not found in Firestore.")

        api_baseurl = doc.to_dict().get("api_baseurl")
        api_key = doc.to_dict().get("api_key")

        if embedding_platform.lower() == "openai":
            return OpenAIEmbeddings(base_url=f"{api_baseurl}/v1", api_key=api_key, model=embedding_model)
        elif embedding_platform.lower() == "ollama":
            return OllamaEmbeddings(base_url=api_baseurl, model=embedding_model)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")


@app.post("/setup/config", tags=["config"])
async def setup_config(request_http: Request, request: SetupConfigRequest, token: str = Depends(verify_bearer_token)):
    valid_models_llm = await get_llm(request.llm)
    valid_models_embedding = await get_llm(request.embedding)
    EMBEDDING = get_embedding(request.embedding, request.model_embedding)

    if request.model_llm not in valid_models_llm:
        raise HTTPException(status_code=400, detail=f"LLM model {request.model_llm} does not exist on platform {request.llm}")
    if request.model_embedding not in valid_models_embedding:
        raise HTTPException(status_code=400, detail=f"Embedding model {request.model_embedding} does not exist on platform {request.embedding}")
    
    if not request.llm or request.llm not in ["openai", "ollama"]:
        raise HTTPException(status_code=400, detail="LLM platform must be 'openai' or 'ollama'.")
    if not request.model_llm:
        raise HTTPException(status_code=400, detail="LLM model cannot be empty.")
    if not request.embedding or request.embedding not in ["openai", "ollama"]:
        raise HTTPException(status_code=400, detail="Embedding platform must be 'openai' or 'ollama'.")
    if not request.model_embedding:
        raise HTTPException(status_code=400, detail="Embedding model cannot be empty.")
    
    if request.chunk_size is None or request.chunk_size <= 0:
        raise HTTPException(status_code=400, detail="Chunk size must be greater than 0 and cannot be empty.")
    if request.chunk_overlap is None or request.chunk_overlap <= 0:
        raise HTTPException(status_code=400, detail="Chunk overlap must be greater than 0 and cannot be empty.")

    try:
        loader = PyPDFDirectoryLoader(DATASETS_DIR)
        documents = loader.load()
        if not documents:
            return api_response(
                request_http,
                status_code=404,
                success=False,
                message="No PDF documents in the datasets directory.",
                data=None
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")

    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=request.chunk_size, chunk_overlap=request.chunk_overlap)
        chunks = text_splitter.split_documents(documents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")

    try:
        vectordb = FAISS.from_documents(chunks, EMBEDDING)
        vectordb.save_local(VECTORDB_DIR)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")

    settings_ref = db.collection("settings").document("models")
    settings_ref.set({
        "llm_platform": request.llm,
        "llm_model": request.model_llm,
        "embedding_platform": request.embedding,
        "embedding_model": request.model_embedding,
        "chunk_size": request.chunk_size,
        "chunk_overlap": request.chunk_overlap,
        "total_chunks": len(chunks),
        "updated_at": firestore.SERVER_TIMESTAMP
    })

    return api_response(
        request_http,
        status_code=200,
        success=True,
        message="Successfully process of load document, chunking, and embeddings.",
        data={
            "llm_platform": request.llm,
            "llm_model": request.model_llm,
            "embedding_platform": request.embedding,
            "embedding_model": request.model_embedding,
            "chunk_size": request.chunk_size,
            "chunk_overlap": request.chunk_overlap,
            "total_chunks": len(chunks)
        }
    )

@app.post("/setup/quick-config", tags=["config"])
async def setup_quick_config(request_http: Request, request: SetupQuickConfigRequest, token: str = Depends(verify_bearer_token)):
    valid_models_llm = await get_llm(request.llm)

    if request.model_llm not in valid_models_llm:
        raise HTTPException(status_code=400, detail=f"LLM model {request.model_llm} does not exist on platform {request.llm}")
    
    if not request.llm or request.llm not in ["openai", "ollama"]:
        raise HTTPException(status_code=400, detail="LLM platform must be 'openai' or 'ollama'.")
    if not request.model_llm:
        raise HTTPException(status_code=400, detail="LLM model cannot be empty.")

    settings_ref = db.collection("settings").document("models")
    settings_ref.set({
        "llm_platform": request.llm,
        "llm_model": request.model_llm,
        "embedding_platform": settings_ref.get().to_dict().get("embedding_platform", ""),
        "embedding_model": settings_ref.get().to_dict().get("embedding_model", ""),
        "chunk_size": settings_ref.get().to_dict().get("chunk_size", 0),
        "chunk_overlap": settings_ref.get().to_dict().get("chunk_overlap", 0),
        "total_chunks": settings_ref.get().to_dict().get("total_chunks", 0),
        "updated_at": firestore.SERVER_TIMESTAMP
    })

    return api_response(
        request_http,
        status_code=200,
        success=True,
        message="Successfully process of LLM models.",
        data={
            "llm_platform": request.llm,
            "llm_model": request.model_llm
        }
    )


@app.get("/check/config", tags=["config"])
async def check_config(request_http: Request, token: str = Depends(verify_bearer_token)):
    try:
        settings_ref = db.collection("settings").document("models")
        doc = settings_ref.get()
        data = doc.to_dict()

        if not doc.exists:
            raise HTTPException(status_code=404, detail="Configuration informations not found in Firestore.")

        updated_at = data.get("updated_at")
        if hasattr(updated_at, "timestamp"):
            gmt8 = timezone(timedelta(hours=8))
            updated_at = updated_at.replace(tzinfo=timezone.utc).astimezone(gmt8).strftime("%Y-%m-%d %H:%M:%S")
        else:
            updated_at = None

        return api_response(
            request_http,
            status_code=200,
            success=True,
            message="Successfully get configuration informations from Firestore.",
            data={
                "llm_platform": data.get("llm_platform"),
                "llm_model": data.get("llm_model"),
                "embedding_platform": data.get("embedding_platform"),
                "embedding_model": data.get("embedding_model"),
                "chunk_size": data.get("chunk_size"),
                "chunk_overlap": data.get("chunk_overlap"),
                "total_chunks": data.get("total_chunks"),
                "updated_at": updated_at
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get configuration informations from Firestore. {str(e)}")


@app.get("/check/openai-models", tags=["config"])
async def check_openai_models(request_http: Request, token: str = Depends(verify_bearer_token)):
    try:
        doc_ref = db.collection("settings").document("connection_openai")
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="OpenAI configuration is not found in Firestore.")

        data = doc.to_dict()
        api_baseurl = data.get("api_baseurl")
        api_key = data.get("api_key")

        if not api_baseurl or not api_key:
            raise HTTPException(status_code=400, detail="API Base URL or API Key OpenAI was not found.")

        response = requests.get(f"{api_baseurl}/v1/models", headers={"Authorization": f"Bearer {api_key}"})

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        models = response.json().get("data", [])

        return api_response(
            request_http,
            status_code=200,
            success=True,
            message="Successfully get the list of OpenAI models.",
            data=[model["id"] for model in models]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/check/ollama-models", tags=["config"])
async def check_openai_models(request_http: Request, token: str = Depends(verify_bearer_token)):
    try:
        doc_ref = db.collection("settings").document("connection_ollama")
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Ollama configuration is not found in Firestore.")

        data = doc.to_dict()
        api_baseurl = data.get("api_baseurl")

        if not api_baseurl:
            raise HTTPException(status_code=400, detail="API Base URL Ollama was not found.")

        response = requests.get(f"{api_baseurl}/v1/models")

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        models = response.json().get("data", [])

        return api_response(
            request_http,
            status_code=200,
            success=True,
            message="Successfully get the list of Ollama models.",
            data=[model["id"] for model in models]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




# Endpoint untuk mendapatkan data dari logs
@app.get("/logs", tags=["logs"])
async def logs(token: str = Depends(verify_bearer_token)):
    try:
        logs_ref = db.collection("logs").order_by("timestamp", direction=firestore.Query.DESCENDING)
        docs = logs_ref.stream()
        data = []

        for doc in docs:
            if isinstance(doc, DocumentSnapshot):
                log_data = doc.to_dict()
                log_data["id"] = doc.id
                if "timestamp" in log_data and log_data["timestamp"] is not None:
                    utc_plus_8 = log_data["timestamp"].astimezone(timezone(timedelta(hours=8)))
                    log_data["timestamp"] = utc_plus_8.strftime("%Y-%m-%d %H:%M:%S")
                data.append(log_data)

        return JSONResponse(
            status_code=200,
            content={
                "statusCode": 200,
                "success": True,
                "message": "OK",
                "data": data
            })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get logs from Firestore {str(e)}")


# Enpoint untuk chat
@app.post("/chat", tags=["chat"])
async def chat_conversation(request: QuestionRequest, request_http: Request, token: str = Depends(verify_bearer_token)):
    timestamp = datetime.now(ZoneInfo("Asia/Makassar")).strftime("%Y-%m-%d %H:%M:%S")
    question = request.question

    if not request.question:
        raise HTTPException(status_code=400, detail="Question must not be empty.")
    
    try:
        _, answers = run_model(question)
        return api_response(
            request_http,
            status_code=200,
            success=True,
            message="OK",
            data=[{
                "timestamp": timestamp,
                "question": question,
                "answer": answers
            }]
        )
    
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"{e.detail}")
    
    except Exception as e:
        return api_response(
            request_http,
            status_code=500,
            success=False,
            message=f"An unexpected error occurred. Try re-embedding, and please try again. If this problem persists, there may be an issue with the LLM or Embedding Service. {str(e)}",
            data=None
        )


app.add_exception_handler(HTTP_404_NOT_FOUND, not_found_handler)
app.add_exception_handler(HTTP_405_METHOD_NOT_ALLOWED, method_not_allowed_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)