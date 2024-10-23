from langgraph.graph import END, START, StateGraph
from utils.create_graph_image import get_graph_image
from src.models import AgentState
from src.config.prompt import *
from dotenv import load_dotenv
from src.agents import *
import os

load_dotenv()

base_url = os.getenv('OLLAMA_BASE_URL')
openai_api_key = os.getenv('OPENAI_API')

def build_graph(question: str):
    workflow = StateGraph(AgentState)
    # level 1
    initial_state = QuestionIdentifierAgent.questionIdentifierAgent({"question": question})

    context = initial_state["activeAgent"]
    
    workflow.add_node("questionIdentifier",  lambda state: initial_state)
    workflow.add_node("writter", WritterAgent.writterAgent)
    workflow.add_edge(START, "questionIdentifier")

    # Apakah workflow bisa dilempar ke fungsi lain???

    if 'account' in context:
        # Level 2
        workflow.add_node("account",  AccountAgent.accountAgent)

        # level 3
        workflow.add_node("accountInfo", AccountAgent.accountInfo)
        workflow.add_node("SSOEmail", AccountAgent.SSOEmailAgent)
        workflow.add_node("UndikshaGoogleEmail", AccountAgent.GoogleEmailAgent)
        workflow.add_node("HybridEmail", AccountAgent.HybridEmailAgent)
        workflow.add_node("incompleteInformation", AccountAgent.incompleteInformationAgent)

        # level 4
        workflow.add_node("resetPassword", SSOEmailAgent.resetPasswordAgent)
        workflow.add_node("identityVerificator", SSOEmailAgent.identityVerificatorAgent)
        workflow.add_node("incompleteSSOStatment", SSOEmailAgent.incompleteSSOStatment)

        # Define Edge
        workflow.add_edge("questionIdentifier", "account")
        workflow.add_edge("resetPassword", "writter")
        workflow.add_edge("identityVerificator", "writter")
        workflow.add_edge("incompleteSSOStatment", "writter")
        workflow.add_conditional_edges(
            "SSOEmail",
            AccountAgent.checkEmailWaslogged, {
                "TRUE": "resetPassword",
                "FALSE": "identityVerificator",
                "NO_INFO" : "incompleteSSOStatment",
            }
        )

        workflow.add_edge("accountInfo", "writter")
        workflow.add_edge("UndikshaGoogleEmail", "writter")
        workflow.add_edge("HybridEmail", "writter")
        workflow.add_edge("incompleteInformation", "writter")
        
        workflow.add_conditional_edges(
            'account',
            AccountAgent.routeToSpecificEmailAgent, {
                'ACCOUNT_INFO': 'accountInfo',
                'SSO_EMAIL': 'SSOEmail',
                'GOOGLE_EMAIL': 'UndikshaGoogleEmail',
                'HYBRID_EMAIL': 'HybridEmail',
                'INCOMPLETE_INFORMATION': 'incompleteInformation',
            }
        )

    if "academic" in context:
        workflow.add_node("academic", AcademicAgent.academicAgent)
        workflow.add_edge("questionIdentifier", "academic")
        workflow.add_edge("academic", "writter")

    if "student" in context:
        workflow.add_node("student", StudentAgent.studentAgent)
        workflow.add_edge("questionIdentifier", "student")
        workflow.add_edge("student", "writter")

    if "news" in context:
        workflow.add_node("news", NewsAgent.newsAgent)
        workflow.add_edge("questionIdentifier", "news")
        workflow.add_edge("news", "writter")

    if "general" in context:
        workflow.add_node("general", GeneralAgent.generalAgent)
        workflow.add_edge("questionIdentifier", "general")
        workflow.add_edge("general", "writter")

    if "out_of_context" in context :
        workflow.add_node("outOfContext", OutOfContextAgent.outOfContextAgent)
        workflow.add_edge("questionIdentifier", "outOfContext")
        workflow.add_edge("outOfContext", "writter")

    workflow.add_edge("writter", END)

    graph = workflow.compile()
    response = graph.invoke({'question': question})
    get_graph_image(graph)

    return response['response']


build_graph("siapa dekan fe undiksha")









