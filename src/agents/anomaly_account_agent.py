from utils.agent_state import AgentState
from utils.debug_time import time_check
from utils.agent_entry import agentEntry


@time_check
def anomalyAccountAgent(state: AgentState):
    info = "\n--- Anomaly Account ---"
    print(info)

    agentEntry(state, "account_agent", ["anomalyAccount_agent"])

    prompt = f"""
        Mohon maaf, saya tidak dapat membantu menangani akun SSO atau Google Undiksha Anda.
        Berikut petunjuk untuk disampaikan kepada pengguna berdasarkan informasi dari akun pengguna:
        - Silahkan datang langsung ke Kantor UPA TIK Undiksha untuk mengurus akun Anda.
        - Atau cek pada kontak kami berikut: https://upttik.undiksha.ac.id/kontak-kami
    """

    agentOpinion = {
        "answer": prompt
    }
    state["finishedAgents"].add("anomalyAccount_agent") 
    return {"answerAgents": [agentOpinion]}
