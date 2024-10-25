from src.models import AgentState
from src.chains import general_chain


class GeneralAgent:
    @staticmethod
    def generalAgent(state: AgentState):
        question = state["question"]
        answer = general_chain(question)
        agent = "GENERAL_AGENT"

        agentOpinion = {
            "agent": agent,
            "answer": answer
        }

        print(f"--- {agent} AGENT ---")
        return {"agentAnswer": [agentOpinion]}
        