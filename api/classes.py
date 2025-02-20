from pydantic import BaseModel
from typing_extensions import List


class QuestionRequest(BaseModel):
    question: str
class DeleteDatasetsRequest(BaseModel):
    filenames: List[str]
class ProcessRequest(BaseModel):
    llm: str
    model_llm: str
    embedder: str
    model_embedder: str
    chunk_size: int
    chunk_overlap: int
    class Config:
        protected_namespaces = ()