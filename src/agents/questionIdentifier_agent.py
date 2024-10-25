import re
from utils.llm import chat_ollama, chat_groq, chat_openai
from src.configs.prompt import QUESTIONIDENTIFIER_PROMPT
from src.models import AgentState
from langchain_core.messages import HumanMessage, SystemMessage
from utils.query_expand import ABBREVIATIONS, expand_abbreviations


class QuestionIdentifierAgent:
    @staticmethod
    def questionIdentifierAgent(state: AgentState) :
        original_question = state['question']
        expanded_question = expand_abbreviations(original_question, ABBREVIATIONS)
        state['question'] = expanded_question
        messages = [
            SystemMessage(content=QUESTIONIDENTIFIER_PROMPT),
            HumanMessage(content=state["question"]),
        ]
        response = chat_openai(messages)
        fixed_response = response.strip().lower()
        activeAgents = re.findall(r'\b\w+\b', fixed_response)

        # print("Original Question:", original_question)
        # print("Expanded Question:", expanded_question)

        print(state["question"])
        print(activeAgents)

        print('--- QUESTION IDENTIFIER AGENT ---\n\n')
        return {"question_type": response, "activeAgent": activeAgents}