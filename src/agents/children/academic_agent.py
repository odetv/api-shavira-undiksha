from src.models import AgentState
from src.chains import academic_chain


class AcademicAgent:
    @staticmethod
    def academicAgent(state: AgentState):
        question = state["question"]
        answer = academic_chain(question)
        agent = "ACADEMIC_AGENT"

        agentOpinion = {
            "agent": agent,
            "answer": answer
        }

        print(f"--- {agent} AGENT ---")
        return {"agentAnswer": [agentOpinion]}