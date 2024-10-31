from operator import add
from typing_extensions import TypedDict, Annotated, Sequence, Optional, Set
from langchain.memory import ConversationBufferMemory


class AnswerState(TypedDict):
    agent = None
    answer = None

class AgentState(TypedDict):
    context: str
    question: str
    question_type: str
    generalContext: str
    generalGraderDocs: str
    generalIsHallucination: str
    responseGeneral: str
    checkKelulusan: str
    noPendaftaran: str
    tglLahirPendaftar: str
    pinPendaftaran: str
    responseIncompleteInfoKelulusan: str
    responseKelulusan: str
    checkKTM: str
    idNIMMhs: str
    urlKTMMhs: str
    responseIncompleteNim: str
    responseKTM: str
    responseOutOfContext: str
    responseFinal: str
    finishedAgents: Set[str]
    answerAgents : Annotated[Sequence[AnswerState], add]

    generalQuestion: str
    newsQuestion: str
    accountQuestion: str
    kelulusanQuestion: str
    ktmQuestion: str
    outOfContextQuestion: str

    newsScrapper: str

    emailAccount: Optional[str] = None
    loginAccountStatus : Optional[str] = None
    checkAccount: str
    responseAccount: str

    memory: ConversationBufferMemory