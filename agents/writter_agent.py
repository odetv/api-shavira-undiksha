from utils.llm import chat_openai
from config.prompt import WRITTER_PROMPT
from models import AgentState

class WritterAgent:
    @staticmethod
    def writterAgent(state: AgentState):
        print(state["agentAnswer"])

        if len(state["agentAnswer"]) == len(state["activeAgent"]):
            print("Ini agen yang aktif", state["activeAgent"])
            print("Ini jawaban dari agen yang aktif", state["agentAnswer"])
            response = chat_openai(
                question=WRITTER_PROMPT.format(question=state["question"], active_agent=state["activeAgent"], agent_answer=state["agentAnswer"]), 
                model='gpt-4o-mini'
            )

            print("\nRespose Dari SHAVIRA:\n", response)
            print('--- WRITTER AGENT ---')