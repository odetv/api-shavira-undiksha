from models import AgentState

class GeneralAgent:
    @staticmethod
    def generalAgent(state: AgentState):
        agent = "GENERAL"
        answer = "Ini jawaban dari general agent"
        agentOpinion = {
            "agent": agent,
            "answer": answer
        }

        print(f"--- {agent} AGENT ---")
        return {"agentAnswer": [agentOpinion]}
        