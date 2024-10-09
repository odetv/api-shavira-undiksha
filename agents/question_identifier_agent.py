import re
from utils.llm import chat_ollama
from config.prompt import QUESTION_IDENTIFIER_PROMPT
from models import AgentState
from langchain_core.messages import HumanMessage, SystemMessage

class QuestionIdentifierAgent:
    @staticmethod
    def getResponseAndContext(question: str) -> str:
        messages = [
            SystemMessage(content=QUESTION_IDENTIFIER_PROMPT),
            HumanMessage(content=question),
        ]

        response = chat_ollama(messages)

        fixed_response = response.strip().lower()

        result = re.findall(r'\b\w+\b', fixed_response)

        return response, result

    @staticmethod
    def questionIdentifierAgent(state: AgentState) :
        response, this_context = QuestionIdentifierAgent.getResponseAndContext(state['question'])
        print(state["question"])
        print(this_context)

        print('--- QUESTION IDENTIFIER AGENT ---\n\n')
        return {"question_type": response, "activeAgent": this_context}