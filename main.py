from langgraph.graph import END, START, StateGraph
from utils.create_graph_image import get_graph_image
from src.models import AgentState
from src.configs.prompt import *
from src.agents import *


def build_graph(question: str):
    workflow = StateGraph(AgentState)
    initial_state = QuestionIdentifierAgent.questionIdentifierAgent({"question": question})
    context = initial_state["activeAgent"]
    workflow.add_node("questionIdentifier_agent",  lambda state: initial_state)
    workflow.add_node("resultWriter_agent", ResultWriterAgent.resultWriterAgent)
    workflow.add_edge(START, "questionIdentifier_agent")

    if "account_agent" in context:
        workflow.add_node("account_agent",  AccountAgent.accountAgent)

        workflow.add_node("accountHelp_agent", AccountAgent.accountHelp)
        workflow.add_node("SSOEmail_agent", AccountAgent.SSOEmailAgent)
        workflow.add_node("UndikshaGoogleEmail_agent", AccountAgent.GoogleEmailAgent)
        workflow.add_node("HybridEmail_agent", AccountAgent.HybridEmailAgent)
        workflow.add_node("incompleteInformation_agent", AccountAgent.incompleteInformationAgent)

        workflow.add_node("resetPassword_agent", SSOEmailAgent.resetPasswordAgent)
        workflow.add_node("identityVerificator_agent", SSOEmailAgent.identityVerificatorAgent)
        workflow.add_node("incompleteSSOStatment_agent", SSOEmailAgent.incompleteSSOStatment)

        workflow.add_edge("questionIdentifier_agent", "account_agent")
        workflow.add_edge("resetPassword_agent", "resultWriter_agent")
        workflow.add_edge("identityVerificator_agent", "resultWriter_agent")
        workflow.add_edge("incompleteSSOStatment_agent", "resultWriter_agent")
        workflow.add_conditional_edges(
            "SSOEmail_agent",
            AccountAgent.checkEmailWaslogged, {
                "TRUE": "resetPassword_agent",
                "FALSE": "identityVerificator_agent",
                "NO_INFO" : "incompleteSSOStatment_agent",
            }
        )
        workflow.add_edge("accountHelp_agent", "resultWriter_agent")
        workflow.add_edge("UndikshaGoogleEmail_agent", "resultWriter_agent")
        workflow.add_edge("HybridEmail_agent", "resultWriter_agent")
        workflow.add_edge("incompleteInformation_agent", "resultWriter_agent")
        workflow.add_conditional_edges(
            "account_agent",
            AccountAgent.routeToSpecificEmailAgent, {
                "ACCOUNTHELP_AGENT": "accountHelp_agent",
                "SSOEMAIL_AGENT": "SSOEmail_agent",
                "GOOGLEEMAIL_AGENT": "UndikshaGoogleEmail_agent",
                "HYBRIDEMAIL_AGENT": "HybridEmail_agent",
                "INCOMPLETEINFORMATION_AGENT": "incompleteInformation_agent",
            }
        )

    if "academic_agent" in context:
        workflow.add_node("academic_agent", AcademicAgent.academicAgent)
        workflow.add_edge("questionIdentifier_agent", "academic_agent")
        workflow.add_edge("academic_agent", "resultWriter_agent")

    if "student_agent" in context:
        workflow.add_node("student_agent", StudentAgent.studentAgent)
        workflow.add_edge("questionIdentifier_agent", "student_agent")
        workflow.add_edge("student_agent", "resultWriter_agent")

    if "news_agent" in context:
        workflow.add_node("news_agent", NewsAgent.newsAgent)
        workflow.add_edge("questionIdentifier_agent", "news_agent")
        workflow.add_edge("news_agent", "resultWriter_agent")

    if "general_agent" in context:
        workflow.add_node("general_agent", GeneralAgent.generalAgent)
        workflow.add_edge("questionIdentifier_agent", "general_agent")
        workflow.add_edge("general_agent", "resultWriter_agent")

    if "kelulusan_agent" in context:
        workflow.add_node("kelulusan_agent", KelulusanAgent.kelulusanAgent)
        workflow.add_node("incompleteInfoKelulusan_agent", KelulusanAgent.incompleteInfoKelulusanAgent)
        workflow.add_node("infoKelulusan_agent", KelulusanAgent.infoKelulusanAgent)
        workflow.add_edge("questionIdentifier_agent", "kelulusan_agent")
        workflow.add_conditional_edges(
            "kelulusan_agent",
            KelulusanAgent.routeToSpecificKelulusanAgent,
            {
                True: "infoKelulusan_agent",
                False: "incompleteInfoKelulusan_agent"
            }
        )
        workflow.add_edge("incompleteInfoKelulusan_agent", "resultWriter_agent")
        workflow.add_edge("infoKelulusan_agent", "resultWriter_agent")

    if "ktm_agent" in context:
        workflow.add_node("ktm_agent", KTMAgent.ktmAgent)
        workflow.add_node("incompleteInfoKTM_agent", KTMAgent.incompleteInfoKTMAgent)
        workflow.add_node("infoKTM_agent", KTMAgent.infoKTMAgent)
        workflow.add_edge("questionIdentifier_agent", "ktm_agent")
        workflow.add_conditional_edges(
            "ktm_agent",
            KTMAgent.routeToSpecificKTMAgent,
            {
                True: "infoKTM_agent",
                False: "incompleteInfoKTM_agent"
            }
        )
        workflow.add_edge("incompleteInfoKTM_agent", "resultWriter_agent")
        workflow.add_edge("infoKTM_agent", "resultWriter_agent")

    if "outofcontext_agent" in context :
        workflow.add_node("outOfContext_agent", OutOfContextAgent.outOfContextAgent)
        workflow.add_edge("questionIdentifier_agent", "outOfContext_agent")
        workflow.add_edge("outOfContext_agent", "resultWriter_agent")

    workflow.add_edge("resultWriter_agent", END)

    graph = workflow.compile()
    response = graph.invoke({"question": question})
    get_graph_image(graph)

    return response["response"]


# DEBUG QUERY EXAMPLES
# build_graph("Siapa rektor undiksha? Bagaimana akademik undiksha? Bagaimana mahasiswa undiksha? apa berita terbaru undiksha? Saya ingin reset password sso undiksha. Saya ingin cetak ktm 2115101014. Saya ingin cek kelulusan nomor pendaftaran 3243000001 tanggal lahir 2006-02-21. Saya ingin bunuh diri")