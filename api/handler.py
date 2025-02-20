from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from utils.logging import log_activity


# Format API response
def api_response(request_http: Request, status_code: int, success: bool, message: str, data=None):
    log_activity({
        "method": f"{request_http.method} {request_http.url.path}",
        "status_code": status_code,
        "success": success,
        "description": f"{message} {data}"
    })
    return JSONResponse(
        content={
            "statusCode": status_code,
            "success": success,
            "message": message,
            "data": data
        }
    )


# Custom handler untuk 404 Not Found
async def not_found_handler(request_http: Request, exc: StarletteHTTPException):
    return api_response(
        request_http,
        status_code=404,
        success=False,
        message=exc.detail,
        data=None
    )


# Custom handler untuk 405 Method Not Allowed
async def method_not_allowed_handler(request_http: Request, exc: StarletteHTTPException):
    return api_response(
        request_http,
        status_code=405,
        success=False,
        message=exc.detail,
        data=None
    )


# General handler untuk validasi error
async def validation_exception_handler(request_http: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_messages = "; ".join([f"{err['loc']}: {err['msg']}" for err in errors])
    return api_response(
        request_http,
        status_code=422,
        success=False,
        message=error_messages,
        data=None
    )


# General handler untuk HTTP Exception lain
async def http_exception_handler(request_http: Request, exc: StarletteHTTPException):
    return api_response(
        request_http,
        status_code=exc.status_code,
        success=False,
        message=exc.detail,
        data=None
    )