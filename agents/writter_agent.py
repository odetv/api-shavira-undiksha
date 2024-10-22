from utils.llm import *
from config.prompt import WRITTER_PROMPT
from models import AgentState
from utils.sort_answer_by_agent import sort_answer_by_agent

class WritterAgent:
    @staticmethod
    def writterAgent(state: AgentState):
        print(state["agentAnswer"])

        if len(state["agentAnswer"]) == len(state["activeAgent"]):
            print("Ini agen yang aktif", state["activeAgent"])
            print("Ini jawaban dari agen yang aktif", state["agentAnswer"])

            sorted_answer = sort_answer_by_agent(state["activeAgent"], state["agentAnswer"])

            print("Ini hasil setelah diurutan pertanyaannya: ", sorted_answer)

            response = chat_openai(
                question=WRITTER_PROMPT.format(question=state["question"], sorted_answer=sorted_answer), 
                model='gpt-4o-mini'
            )

            # response = chat_groq(
            #     question=WRITTER_PROMPT.format(question=state["question"], sorted_answer=sorted_answer), 
            # )

            state["response"] = response

            print("\nRespose Dari SHAVIRA:\n", response)
            print('--- WRITTER AGENT ---\n\n')

            return state

        else :
            agent = state["agentAnswer"][0]["agent"]
            print("AGEN SUDAH SELESAI MEMBERIKAN JAWABAN: ", agent)