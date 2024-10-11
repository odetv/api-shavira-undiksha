from models import AgentState

class NewsAgent:
    @staticmethod
    def newsAgent(state: AgentState):
        agent = "NEWS AGENT"
        answer = "ini jawaban dari NEWS AGENT agent"
        agentOpinion = {
            "agent": agent,
            "answer": answer
        }

        print("--- NEWS AGENT ---")   
        return {"agentAnswer": [agentOpinion]}