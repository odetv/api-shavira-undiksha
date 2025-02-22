from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.metadata import tags_metadata


app = FastAPI(
    openapi_tags=tags_metadata,
    title="API Shavira Undiksha",
    summary="API Shavira (Ganesha Virtual Assistant) Undiksha",
    version="0.0.1",
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapishavira.json"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)