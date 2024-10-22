from models import AgentState
from utils.llm import chat_groq
from config.prompt import GENERAL_AGENT_PROMPT
from chain import general_chain

class GeneralAgent:
    @staticmethod
    def generalAgent(state: AgentState):
        answer = general_chain(state["question"])
        agent = "GENERAL"

        agentOpinion = {
            "agent": agent,
            "answer": answer
        }

        print(f"--- {agent} AGENT ---")
        return {"agentAnswer": [agentOpinion]}
        