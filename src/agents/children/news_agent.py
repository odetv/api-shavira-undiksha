from src.models import AgentState

class NewsAgent:
    @staticmethod
    def newsAgent(state: AgentState):
        answer = "ini jawaban dari NEWS AGENT agent"
        agent = "NEWS_AGENT"
        
        agentOpinion = {
            "agent": agent,
            "answer": answer
        }

        print("--- NEWS AGENT ---")   
        return {"agentAnswer": [agentOpinion]}