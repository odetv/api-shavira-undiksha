import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security.api_key import APIKeyHeader
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_405_METHOD_NOT_ALLOWED
from fastapi.exceptions import RequestValidationError
from dotenv import load_dotenv
from pydantic import BaseModel
from main import build_graph


load_dotenv()
chatbot_api_key = os.getenv("VA_API_KEY")
chatbot_api_key_header = APIKeyHeader(name="VA-API-KEY")


def verify_api_key(header_key: str = Depends(chatbot_api_key_header)):
    if header_key != chatbot_api_key:
        raise HTTPException(status_code=401, detail="Eitss... mau ngapain? API Key salah. Hubungi admin untuk mendapatkan API Key!")


app = FastAPI()
class QuestionRequest(BaseModel):
    question: str
class QuestionResponse(BaseModel):
    question: str
    answer: str


def api_response(status_code: int, success: bool, message: str, data=None):
    return JSONResponse(
        status_code=status_code,
        content={
            "statusCode": status_code,
            "success": success,
            "message": message,
            "data": data
        }
    )

@app.get("/")
async def root():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "timestamp": current_time,
        "message": "API Virtual Assistant Undiksha",
        "hint": "Diperlukan API Key CHATBOT-API-KEY untuk menggunakan API ini!"
    }
    


@app.post("/chat")
def chat_endpoint(request: QuestionRequest, api_key: str = Depends(verify_api_key)):
    question = request.question
    try:
        answer = build_graph(question)
        return api_response(
            status_code=200,
            success=True,
            message="OK",
            data=[{
                "question": question,
                "answer": answer
            }]
        )
    except HTTPException as e:
        return api_response(
            status_code=e.status_code,
            success=False,
            message=f"Failed: {e.detail}",
            data=None
        )
    except Exception as e:
        return api_response(
            status_code=500,
            success=False,
            message=f"Failed: {str(e)}",
            data=None
        )


# Custom handler untuk 404 Not Found
@app.exception_handler(HTTP_404_NOT_FOUND)
async def not_found_handler(request: Request, exc: StarletteHTTPException):
    return api_response(
        status_code=404,
        success=False,
        message="Failed: Not Found",
        data=None
    )


# Custom handler untuk 405 Method Not Allowed
@app.exception_handler(HTTP_405_METHOD_NOT_ALLOWED)
async def method_not_allowed_handler(request: Request, exc: StarletteHTTPException):
    return api_response(
        status_code=405,
        success=False,
        message="Failed: Method Not Allowed",
        data=None
    )


# General handler untuk HTTP Exception lain
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return api_response(
        status_code=exc.status_code,
        success=False,
        message=f"Failed: {exc.detail}",
        data=None
    )


# General handler untuk validasi error
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_messages = "; ".join([f"{err['loc']}: {err['msg']}" for err in errors])

    return api_response(
        status_code=422,
        success=False,
        message=f"Failed: Validation Error - {error_messages}",
        data=None
    )


# DEBUG
# uvicorn api:app --reload
