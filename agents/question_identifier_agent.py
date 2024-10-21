import re
from utils.llm import chat_ollama, chat_groq
from config.prompt import QUESTION_IDENTIFIER_PROMPT
from models import AgentState
from langchain_core.messages import HumanMessage, SystemMessage

class QuestionIdentifierAgent:
    @staticmethod
    def questionIdentifierAgent(state: AgentState) :
        messages = [
            SystemMessage(content=QUESTION_IDENTIFIER_PROMPT),
            HumanMessage(content=state["question"]),
        ]

        response = chat_groq(messages)

        fixed_response = response.strip().lower()

        activeAgents = re.findall(r'\b\w+\b', fixed_response)

        print(state["question"])
        print(activeAgents)

        print('--- QUESTION IDENTIFIER AGENT ---\n\n')
        return {"question_type": response, "activeAgent": activeAgents}