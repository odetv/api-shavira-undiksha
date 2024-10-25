from typing_extensions import TypedDict, Literal, Optional, Annotated, Sequence
from operator import add

class AnswerState(TypedDict):
    agent = None
    answer = None

class AgentState(TypedDict):
    context = None
    question_type : Optional[str] = None
    question : str
    response : Optional[str] = None
    email: Optional[str] = None
    loginStatus : Optional[str] = None
    accountType : Optional[str] = None
    incompleteReason : Optional[str] = None
    accountAgentType : Optional[str] = None
    agentAnswer : Annotated[Sequence[AnswerState], add]
    activeAgent : Optional[list] = None
    checkKelulusan: str
    noPendaftaran: str
    tglLahirPendaftar: str
    responseIncompleteInfoKelulusan: str
    responseKelulusan: str
    checkKTM: str
    idNIMMhs: str
    urlKTMMhs: str
    responseIncompleteNim: str
    responseKTM: str

