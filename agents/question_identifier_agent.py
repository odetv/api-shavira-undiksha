import re
from utils.llm import chat_ollama, chat_groq, chat_openai
from config.prompt import QUESTION_IDENTIFIER_PROMPT
from models import AgentState
from langchain_core.messages import HumanMessage, SystemMessage

class QuestionIdentifierAgent:
    @staticmethod
    def questionIdentifierAgent(state: AgentState) :
        # response = chat_groq(messages)
        response = chat_openai(state['question'], QUESTION_IDENTIFIER_PROMPT, model='gpt-4o-mini')

        fixed_response = response.strip().lower()

        activeAgents = re.findall(r'\b\w+\b', fixed_response)

        print(state["question"])
        print(activeAgents)

        print('--- QUESTION IDENTIFIER AGENT ---\n\n')
        return {"question_type": response, "activeAgent": activeAgents}