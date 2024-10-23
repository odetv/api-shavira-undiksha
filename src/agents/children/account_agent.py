from src.models import AgentState
from utils.llm import chat_openai, chat_ollama, chat_groq
from src.config.prompt import ACCOUNT_PROMPT, INCOMPLETE_PROMPT, ACCOUNT_INFO_PROMPT
import json

class AccountAgent:
    @staticmethod
    def accountAgent(state: AgentState):
        message = ACCOUNT_PROMPT.format(question=state['question'])

        response = chat_openai(question=message, model='gpt-4o-mini')

        result = [item.strip() for item in response.split(",")]

        print(response)

        try:    
            email = result[0]
            emailType = result[1]
            loginStatus = result[2]
            print("email: ", email)
            print("emailType: ", emailType)
            print("loginStatus: ", loginStatus)
            validUndikshaEmail = email and (email.endswith("@undiksha.ac.id") or email.endswith("@student.undiksha.ac.id"))
            reason = None

            
            if "null" not in email and "ACCOUNT_INFO" not in emailType: # Cek apakah email dan emailType bukan INCOMPLETE INFORMATION atau tidak None
                if validUndikshaEmail:
                    if emailType == 'SSO_EMAIL':
                        accountAgentType = "SSO_EMAIL"
                    elif emailType == 'GOOGLE_EMAIL':
                        accountAgentType = "GOOGLE_EMAIL"
                    elif emailType == 'HYBRID_EMAIL':
                        accountAgentType = "HYBRID_EMAIL"
                    else:
                        accountAgentType = "INCOMPLETE_INFORMATION"
                        reason = "Tidak disebutkan apakah user ingin reset password Akun google Undiksha atau SSO E-Ganesha"
                else:
                    accountAgentType = "INCOMPLETE_INFORMATION"
                    reason = 'Email yang diinputkan bukan email undiksha, mohon gunakan email undiksha dengan domain @undiksha.ac.id atau @student.undiksha.ac.id'
                    
            else:
                if "ACCOUNT_INFO" in emailType:
                    accountAgentType = "ACCOUNT_INFO"
                else:
                    accountAgentType = "INCOMPLETE_INFORMATION"
                    reason = 'user tidak menyebutkan alamat email'
                
            print(f"Alasan incomplete: {reason}")
            print('--- ACCOUNT AGENT ---\n\n')
            return {"accountAgentType": accountAgentType, "incompleteReason": reason, "loginStatus": loginStatus}

        except json.JSONDecodeError as e:
            # Handle the case where the response is not valid JSON
            print(f"Err: {e}")
            
    @staticmethod
    def routeToSpecificEmailAgent(state: AgentState):
        return state['accountAgentType']

    @staticmethod
    def checkEmailWaslogged(state: AgentState):
        return state['loginStatus']
    
    @staticmethod
    def accountInfo(state: AgentState):
        prompt = ACCOUNT_INFO_PROMPT.format(question=state['question'])

        response = chat_groq(prompt)

        agent = "ACCOUNT"

        agentOpinion = {
            "agent": agent,
            "answer": response
        }

        print(f"--- {agent} INFO AGENT ---")
        return {"agentAnswer": [agentOpinion]}

    @staticmethod
    def SSOEmailAgent(state: AgentState):
        agent = "ACCOUNT"

        agentOpinion = {
            "agent": agent,
            "answer": "Email telah direset silahkan akses email undiksha melalui gmail"
        }

        print('--- SSO EMAIL AGENT ---')


    @staticmethod
    def GoogleEmailAgent(state: AgentState):
        print('--- GOOGLE EMAIL AGENT ---')

    @staticmethod
    def HybridEmailAgent(state: AgentState):
        print('--- HYBRID EMAIL AGENT ---')

    @staticmethod
    def incompleteInformationAgent(state: AgentState):
        response = chat_groq(
            question=INCOMPLETE_PROMPT.format(question=state['question'], reason=state['incompleteReason']), 
        )

        agent = "ACCOUNT"

        agentOpinion = {
            "agent": agent,
            "answer": response
        }

        print('--- INCOMPLETE INFORMATION AGENT ---')
        return {"agentAnswer": [agentOpinion]}
    
    