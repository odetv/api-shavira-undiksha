from models import AgentState

class SSOEmailAgent:
    @staticmethod
    def resetPasswordAgent(state: AgentState):
        print("-- RESET PASSWORD AGENT --")
        agent = "ACCOUNT"
        answer = "Proses reset password ..."
        agentOpinion = {
            "agent": agent,
            "answer": answer
        }
        print("-- RESET PASSWORD AGENT --")
        return {"agentAnswer": [agentOpinion]}

    @staticmethod
    def identityVerificatorAgent(state: AgentState):
        print("-- IDENTITY VERIFICATOR AGENT --")


    @staticmethod
    def incompleteSSOStatment(state: AgentState):
        print("-- INCOMPLETE SSO STATEMENT --")

        agent = "ACCOUNT"
        answer = "Tanyakan apakah akun undiksha tersebut sudah diloginkan di perangkatnya?"
        agentOpinion = {
            "agent": agent,
            "answer": answer
        }

        return {"agentAnswer": [agentOpinion]}