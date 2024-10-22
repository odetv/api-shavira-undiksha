from models import AgentState
from utils.llm import chat_groq
from config.prompt import GENERAL_AGENT_PROMPT

class GeneralAgent:
    @staticmethod
    def generalAgent(state: AgentState):
        prompt = GENERAL_AGENT_PROMPT.format(question=state["question"])
        answer = chat_groq(prompt)
        agent = "GENERAL"

        agentOpinion = {
            "agent": agent,
            "answer": answer
        }

        print(f"--- {agent} AGENT ---")
        return {"agentAnswer": [agentOpinion]}
        