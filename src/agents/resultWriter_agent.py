from utils.llm import *
from src.configs.prompt import RESULTWRITER_PROMPT
from src.models import AgentState
from langchain_core.messages import HumanMessage, SystemMessage
from utils.sort_answer_by_agent import sort_answer_by_agent

class ResultWriterAgent:
    @staticmethod
    def resultWriterAgent(state: AgentState):
        print(state["agentAnswer"])

        if len(state["agentAnswer"]) == len(state["activeAgent"]):
            print("Ini agen yang aktif", state["activeAgent"])
            print("Ini jawaban dari agen yang aktif", state["agentAnswer"])

            sorted_answer = sort_answer_by_agent(state["activeAgent"], state["agentAnswer"])

            print("Ini hasil setelah diurutan pertanyaannya: ", sorted_answer)

            question=RESULTWRITER_PROMPT.format(question=state["question"], sorted_answer=sorted_answer)

            messages = [
                HumanMessage(question)
            ]

            response = chat_openai(messages)

            # response = chat_groq(
            #     question=RESULTWRITER_PROMPT.format(question=state["question"], sorted_answer=sorted_answer), 
            # )

            state["response"] = response

            print("\nRespose Dari SHAVIRA:\n", response)
            print('--- WRITTER AGENT ---\n\n')

            return state

        