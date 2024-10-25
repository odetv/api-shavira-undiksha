from src.models import AgentState

class OutOfContextAgent:
    @staticmethod
    def outOfContextAgent(state: AgentState):
        answer = "Pertanyaan pengguna diluar dari konteks kamu sebagai Virtual assisten untuk helpdesk undiksha, kamu hanya diijinkan untuk menjawab terkait layanan helpdesk Undiksha"
        agent = "OUTOFCONTEXT_AGENT"
        
        agentOpinion = {
            "agent": agent,
            "answer": answer
        }

        print("--- OUT OF CONTEXT AGENT ---")    
        return {"agentAnswer": [agentOpinion]}