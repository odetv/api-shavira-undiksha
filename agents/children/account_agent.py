from models import AgentState
from utils.llm import chat_openai, chat_ollama
from config.prompt import ACCOUNT_PROMPT, INCOMPLETE_PROMPT
import json

class AccountAgent:
    @staticmethod
    def accountAgent(state: AgentState):
        message = ACCOUNT_PROMPT.format(question=state['question'])

        response = chat_openai(question=message, model='gpt-4o-mini')

        result = [item.strip() for item in response.split(",")]

        try:    
            email = result[0]
            emailType = result[1]
            loginStatus = result[2]
            print("email: ", email)
            print("emailType: ", emailType)
            print("loginStatus: ", loginStatus)
            validUndikshaEmail = email and (email.endswith("@undiksha.ac.id") or email.endswith("@student.undiksha.ac.id"))
            reason = None

            if "null" not in email: # Cek apakah email dan emailType bukan INCOMPLETE INFORMATION atau tidak None
                if validUndikshaEmail:
                    if emailType == 'SSO_EMAIL':
                        resetPasswordType = "SSO_EMAIL"
                    elif emailType == 'GOOGLE_EMAIL':
                        resetPasswordType = "GOOGLE_EMAIL"
                    elif emailType == 'HYBRID_EMAIL':
                        resetPasswordType = "HYBRID_EMAIL"
                    else:
                        resetPasswordType = "INCOMPLETE_INFORMATION"
                        reason = "Tidak disebutkan apakah user ingin reset password Akun google Undiksha atau SSO E-Ganesha"
                else:
                    resetPasswordType = "INCOMPLETE_INFORMATION"
                    reason = 'Email yang diinputkan bukan email undiksha, mohon gunakan email undiksha dengan domain @undiksha.ac.id atau @student.undiksha.ac.id'
                    
            else:
                resetPasswordType = "INCOMPLETE_INFORMATION"
                reason = 'user tidak menyebutkan alamat email'
                
            print(f"Alasan incomplete: {reason}")
            print('--- ACCOUNT AGENT ---\n\n')
            return {"resetPasswordType": resetPasswordType, "incompleteReason": reason, "loginStatus": loginStatus}

        except json.JSONDecodeError as e:
            # Handle the case where the response is not valid JSON
            print(f"Err: {e}")
            
    @staticmethod
    def routeToSpecificEmailAgent(state: AgentState):
        return state['resetPasswordType']

    @staticmethod
    def checkEmailWaslogged(state: AgentState):
        return state['loginStatus']
    
    @staticmethod
    def SSOEmailAgent(state: AgentState):
        print('--- SSO EMAIL AGENT ---')

    @staticmethod
    def GoogleEmailAgent(state: AgentState):
        print('--- GOOGLE EMAIL AGENT ---')

    @staticmethod
    def HybridEmailAgent(state: AgentState):
        print('--- HYBRID EMAIL AGENT ---')

    @staticmethod
    def incompleteInformationAgent(state: AgentState):
        response = chat_ollama(
            question=INCOMPLETE_PROMPT.format(question=state['question'], reason=state['incompleteReason']), 
            model='gemma2'
        )

        agent = "ACCOUNT"

        agentOpinion = {
            "agent": agent,
            "answer": response
        }

        print('--- INCOMPLETE INFORMATION AGENT ---')
        return {"agentAnswer": [agentOpinion]}
    
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


