from models import AgentState

class OutOfContextAgent:
    @staticmethod
    def outOfContextAgent(state: AgentState):
        agent = "OUT OF CONTEXT"
        answer = "ini jawaban dari OUT OF CONTEXT agent"
        agentOpinion = {
            "agent": agent,
            "answer": answer
        }

        print("--- OUT OF CONTEXT AGENT ---")    
        return {"agentAnswer": [agentOpinion]}


        