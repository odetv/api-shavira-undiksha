from src.models import AgentState
from src.chains import student_chain


class StudentAgent:
    @staticmethod
    def studentAgent(state: AgentState):
        question = state["question"]
        answer = student_chain(question)
        agent = "STUDENT_AGENT"
        
        agentOpinion = {
            "agent": agent,
            "answer": answer
        }

           
        print("-- STUDENT AGENT --")
        return {"agentAnswer": [agentOpinion]}