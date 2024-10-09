from langgraph.graph import END, START, StateGraph
from utils.graph_image import get_graph_image
from models import AgentState
from langchain_community.llms import Ollama
from config.prompt import *
from dotenv import load_dotenv
from agents import *
import os


load_dotenv()

base_url = os.getenv('BASE_URL')
openai_api_key = os.getenv('OPENAI_API')

def build_graph(question):
    workflow = StateGraph(AgentState)
    # level 1
    workflow.add_node("questionIdentifier", QuestionIdentifierAgent.questionIdentifierAgent)
    workflow.add_node("writter", WritterAgent.writterAgent)
    workflow.add_edge(START, "questionIdentifier")

    # Apakah workflow bisa dilempar ke fungsi lain???

    _, context = QuestionIdentifierAgent.getResponseAndContext(question)

    if 'account' in context:
        # Level 2
        workflow.add_node("account", AccountAgent.accountAgent)

        # level 3
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

        workflow.add_edge("UndikshaGoogleEmail", "writter")
        workflow.add_edge("HybridEmail", "writter")
        workflow.add_edge("incompleteInformation", "writter")
        
        workflow.add_conditional_edges(
            'account',
            AccountAgent.routeToSpecificEmailAgent, {
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
    graph.invoke({'question': question})
    get_graph_image(graph)

build_graph("saya ingin restpassword akun pada akun sso undiksha asiapp@undiksha.ac.id dan saya sudah loginkan di perangkat hp")






