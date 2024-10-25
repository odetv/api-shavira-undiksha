from src.models import AgentState
from utils.llm import chat_openai, chat_ollama, chat_groq
from langchain_core.messages import HumanMessage, SystemMessage
from src.configs.prompt import ACCOUNT_PROMPT, INCOMPLETEACCOUNT_PROMPT, ACCOUNTHELP_PROMPT
import json


class AccountAgent:
    @staticmethod
    def accountAgent(state: AgentState):
        message = ACCOUNT_PROMPT.format(question=state['question'])

        messages = [
            HumanMessage(content=message)
        ]

        response = chat_openai(messages)

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

            
            if "null" not in email and "ACCOUNTHELP_AGENT" not in emailType: # Cek apakah email dan emailType bukan INCOMPLETE INFORMATION atau tidak None
                if validUndikshaEmail:
                    if emailType == 'SSOEMAIL_AGENT':
                        accountAgentType = "SSOEMAIL_AGENT"
                    elif emailType == 'GOOGLEEMAIL_AGENT':
                        accountAgentType = "GOOGLEEMAIL_AGENT"
                    elif emailType == 'HYBRIDEMAIL_AGENT':
                        accountAgentType = "HYBRIDEMAIL_AGENT"
                    else:
                        accountAgentType = "INCOMPLETEINFORMATION_AGENT"
                        reason = "Tidak disebutkan apakah user ingin reset password Akun google Undiksha atau SSO E-Ganesha"
                else:
                    accountAgentType = "INCOMPLETEINFORMATION_AGENT"
                    reason = 'Email yang diinputkan bukan email undiksha, mohon gunakan email undiksha dengan domain @undiksha.ac.id atau @student.undiksha.ac.id'
                    
            else:
                if "ACCOUNTHELP_AGENT" in emailType:
                    accountAgentType = "ACCOUNTHELP_AGENT"
                else:
                    accountAgentType = "INCOMPLETEINFORMATION_AGENT"
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
    def accountHelp(state: AgentState):
        prompt = ACCOUNTHELP_PROMPT.format(question=state['question'])

        messages = [
            HumanMessage(content=prompt)
        ]

        response = chat_openai(messages)

        agent = "ACCOUNT_AGENT"

        agentOpinion = {
            "agent": agent,
            "answer": response
        }

        print(f"--- {agent} INFO AGENT ---")
        return {"agentAnswer": [agentOpinion]}

    @staticmethod
    def SSOEmailAgent(state: AgentState):
        agent = "ACCOUNT_AGENT"

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
        question=INCOMPLETEACCOUNT_PROMPT.format(question=state['question'], reason=state['incompleteReason'])
        messages = [
            HumanMessage(content=question)
        ]
        response = chat_openai(messages)

        agent = "ACCOUNT_AGENT"

        agentOpinion = {
            "agent": agent,
            "answer": response
        }

        print('--- INCOMPLETE INFORMATION AGENT ---')
        return {"agentAnswer": [agentOpinion]}
    
    