from models import AgentState

class StudentAgent:
    @staticmethod
    def studentAgent(state: AgentState):
        agent = "STUDENT"
        answer = "ini jawaban dari student agent"
        agentOpinion = {
            "agent": agent,
            "answer": answer
        }

           
        print("-- STUDENT AGENT --")
        return {"agentAnswer": [agentOpinion]}