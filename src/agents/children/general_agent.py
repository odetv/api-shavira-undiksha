from src.models import AgentState
from utils.llm import chat_groq
from src.config.prompt import GENERAL_AGENT_PROMPT
from src.chain import general_chain

class GeneralAgent:
    @staticmethod
    def generalAgent(state: AgentState):
        question = state["question"]
        answer = general_chain(question)
        agent = "GENERAL"

        agentOpinion = {
            "agent": agent,
            "answer": answer
        }

        print(f"--- {agent} AGENT ---")
        return {"agentAnswer": [agentOpinion]}
        