from typing import TypedDict, Literal, Optional, Annotated, Sequence
from operator import add

class AnswerState(TypedDict):
    agent = None
    answer = None

class AgentState(TypedDict):
    context = None
    question_type : Optional[str] = None
    question : str
    email: Optional[str] = None
    loginStatus : Optional[str] = None
    accountType : Optional[str] = None
    incompleteReason : Optional[str] = None
    resetPasswordType : Optional[str] = None
    agentAnswer : Annotated[Sequence[AnswerState], add]
    activeAgent : Optional[list] = None