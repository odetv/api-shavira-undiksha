import re
from utils.agent_state import AgentState
from utils.api_undiksha import show_ktm_mhs
from utils.debug_time import time_check

class InfoKTMAgent:
    @time_check
    @staticmethod
    def infoKTMAgent(state: AgentState):
        info = "\n--- Info KTM ---"
        print(info)

        nim_match = re.search(r"\b(?:ktm|kartu tanda mahasiswa)\s*.*?(\b\d{10}\b)(?!\d)", state["ktmQuestion"], re.IGNORECASE)
        state["idNIMMhs"] = nim_match.group(1)
        id_nim_mhs = state.get("idNIMMhs", "ID NIM tidak berhasil didapatkan.")
        url_ktm_mhs = show_ktm_mhs(state)
        
        response = f"""
            Berikut informasi Kartu Tanda Mahasiswa (KTM) Anda.
            - NIM: {id_nim_mhs}
            - Download KTM: {url_ktm_mhs}
        """

        agentOpinion = {
            "answer": response
        }

        state["finishedAgents"].add("infoKTM_agent")
        state["responseKTM"] = response
        return {"answerAgents": [agentOpinion]}