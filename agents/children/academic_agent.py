from models import AgentState

class AcademicAgent:
    @staticmethod
    def academicAgent(state: AgentState):
        agent = "ACADEMIC"
        answer = "jawaban dari academic agent"
        agentOpinion = {
            "agent": agent,
            "answer": answer
        }

        print("-- ACADEMIC AGENT --")
        return {"agentAnswer": [agentOpinion]}
