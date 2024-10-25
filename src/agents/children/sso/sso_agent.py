from src.models import AgentState

class SSOEmailAgent:
    @staticmethod
    def resetPasswordAgent(state: AgentState):
        print("-- RESET PASSWORD AGENT --")
        agent = "ACCOUNT_AGENT"
        answer = "Proses reset password berhasil, silahkan cek email anda dan klik link reset passwordnya"
        agentOpinion = {
            "agent": agent,
            "answer": answer
        }
        print("-- RESET PASSWORD AGENT --")
        return {"agentAnswer": [agentOpinion]}

    @staticmethod
    def identityVerificatorAgent(state: AgentState):
        print("-- IDENTITY VERIFICATOR AGENT --")

        agent = "ACCOUNT_AGENT"
        answer = "Minta untuk mengirimkan foto identitas dengan KTP"
        agentOpinion = {
            "agent": agent,
            "answer": answer
        }

        print("-- IDENTITY VERIFICATOR AGENT --")
        return {"agentAnswer": [agentOpinion]}


    @staticmethod
    def incompleteSSOStatment(state: AgentState):
        print("-- INCOMPLETE SSO STATEMENT --")

        agent = "ACCOUNT_AGENT"
        answer = "Tanyakan apakah akun undiksha tersebut sudah diloginkan di perangkatnya?"
        agentOpinion = {
            "agent": agent,
            "answer": answer
        }

        return {"agentAnswer": [agentOpinion]}


