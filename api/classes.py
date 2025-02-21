from pydantic import BaseModel
from typing_extensions import List


class QuestionRequest(BaseModel):
    question: str

class DeleteDatasetsRequest(BaseModel):
    filenames: List[str]

class SetupConfigRequest(BaseModel):
    llm: str
    model_llm: str
    embedding: str
    model_embedding: str
    chunk_size: int
    chunk_overlap: int
    class Config:
        protected_namespaces = ()

class SetupQuickConfigRequest(BaseModel):
    llm: str
    model_llm: str
    class Config:
        protected_namespaces = ()