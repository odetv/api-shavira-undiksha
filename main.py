import re
from langgraph.graph import END, START, StateGraph
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.vectorstores import FAISS
from utils.agent_state import AgentState
from utils.llm import chat_llm, embedder
from utils.api_undiksha import show_reset_sso, show_ktm_mhs, show_kelulusan_pmb
from utils.create_graph_image import get_graph_image
from utils.debug_time import time_check
from utils.expansion import query_expansion, CONTEXT_ABBREVIATIONS
from utils.scrapper_rss import scrap_news
from src.config.config import VECTORDB_DIR
from src.agents import *


@time_check
def build_graph(question):
    workflow = StateGraph(AgentState)
    initial_state = QuestionIdentifierAgent.questionIdentifierAgent({"question": question, "finishedAgents": set()})
    context = initial_state["question_type"]
    workflow.add_node("questionIdentifier_agent", lambda x: initial_state)
    workflow.add_node("resultWriter_agent", ResultWriterAgent.resultWriterAgent)
    workflow.add_edge(START, "questionIdentifier_agent")

    if "general_agent" in context:
        workflow.add_node("general_agent", GeneralAgent.generalAgent)
        workflow.add_node("graderDocs_agent", GraderDocsAgent.graderDocsAgent)
        workflow.add_node("answerGeneral_agent", AnswerGeneralAgent.answerGeneralAgent)
        workflow.add_edge("questionIdentifier_agent", "general_agent")
        workflow.add_edge("general_agent", "graderDocs_agent")
        workflow.add_edge("graderDocs_agent", "answerGeneral_agent")
        workflow.add_edge("answerGeneral_agent", "resultWriter_agent")

    if "news_agent" in context:
        workflow.add_node("news_agent", NewsAgent.newsAgent)
        workflow.add_edge("questionIdentifier_agent", "news_agent")
        workflow.add_edge("news_agent", "resultWriter_agent")

    if "account_agent" in context:
        workflow.add_node("account_agent", AccountAgent.accountAgent)
        workflow.add_node("resetAccount_agent", ResetAccountAgent.resetAccountAgent)
        workflow.add_node("incompleteAccount_agent", IncompleteAccountAgent.incompleteAccountAgent)
        workflow.add_node("anomalyAccount_agent", AnomalyAccountAgent.anomalyAccountAgent)
        workflow.add_edge("questionIdentifier_agent", "account_agent")
        workflow.add_conditional_edges(
            "account_agent",
            lambda state: state["checkAccount"],
            {
                "reset": "resetAccount_agent",
                "incomplete": "incompleteAccount_agent",
                "anomaly": "anomalyAccount_agent"
            }
        )
        workflow.add_edge("resetAccount_agent", "resultWriter_agent")
        workflow.add_edge("incompleteAccount_agent", "resultWriter_agent")
        workflow.add_edge("anomalyAccount_agent", "resultWriter_agent")

    if "kelulusan_agent" in context:
        workflow.add_node("kelulusan_agent", KelulusanAgent.kelulusanAgent)
        workflow.add_node("incompleteInfoKelulusan_agent", IncompleteInfoKelulusanAgent.incompleteInfoKelulusanAgent)
        workflow.add_node("infoKelulusan_agent", InfoKelulusanAgent.infoKelulusanAgent)
        workflow.add_edge("questionIdentifier_agent", "kelulusan_agent")
        workflow.add_conditional_edges(
            "kelulusan_agent",
            lambda state: state["checkKelulusan"],
            {
                True: "infoKelulusan_agent",
                False: "incompleteInfoKelulusan_agent"
            }
        )
        workflow.add_edge("incompleteInfoKelulusan_agent", "resultWriter_agent")
        workflow.add_edge("infoKelulusan_agent", "resultWriter_agent")

    if "ktm_agent" in context:
        workflow.add_node("ktm_agent", KtmAgent.ktmAgent)
        workflow.add_node("incompleteInfoKTM_agent", IncompleteInfoKTMAgent.incompleteInfoKTMAgent)
        workflow.add_node("infoKTM_agent", InfoKTMAgent.infoKTMAgent)
        workflow.add_edge("questionIdentifier_agent", "ktm_agent")
        workflow.add_conditional_edges(
            "ktm_agent",
            lambda state: state["checkKTM"],
            {
                True: "infoKTM_agent",
                False: "incompleteInfoKTM_agent"
            }
        )
        workflow.add_edge("incompleteInfoKTM_agent", "resultWriter_agent")
        workflow.add_edge("infoKTM_agent", "resultWriter_agent")

    workflow.add_node("graderHallucinations_agent", GraderHallucinationsAgent.graderHallucinationsAgent)
    workflow.add_edge("resultWriter_agent", "graderHallucinations_agent")
    workflow.add_conditional_edges(
        "graderHallucinations_agent",
        lambda state: state["isHallucination"] and state["generalHallucinationCount"] < 2 if state["isHallucination"] else False,
        {
            True: "resultWriter_agent",
            False: END,
        }
    )

    graph = workflow.compile()
    result = graph.invoke({"question": question})
    answers = result.get("responseFinal", [])
    contexts = result.get("answerAgents", "")
    get_graph_image(graph)
    return contexts, answers



# DEBUG QUERY EXAMPLES
# build_graph("Siapa rektor undiksha? Berikan 1 berita saja. Saya lupa password sso email@undiksha.ac.id sudah ada akun google di hp. Cetak ktm 1234567890. Cek kelulusan nomor pendaftaran 1234567890 tanggal lahir 2001-01-31.")
# build_graph("Saya lupa password sso sudiartika@undiksha.ac.id sudah ada akun google di hp.")
# build_graph("Cek kelulusan nomor pendaftaran 1234567890 tanggal lahir 2001-01-31.")
build_graph("Cetak ktm 1234567890")