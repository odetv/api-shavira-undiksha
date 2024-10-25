import re
from src.models import AgentState
from utils.api_undiksha import show_ktm_mhs
from utils.llm import chat_openai, chat_ollama, chat_groq
from langchain_core.messages import HumanMessage, SystemMessage


class KTMAgent:
    def ktmAgent(state: AgentState):
        info = "\n--- KTM ---"
        print(info)

        prompt = """
            Anda adalah seoarang analis informasi Kartu Tanda Mahasiswa (KTM).
            Tugas Anda adalah mengklasifikasikan jenis pertanyaan pada konteks Undiksha (Universitas Pendidikan Ganesha).
            NIM (Nomor Induk Mahasiswa) yang valid dari Undiksha berjumlah 10 digit angka.
            Sekarang tergantung pada jawaban Anda, akan mengarahkan ke agent yang tepat.
            Ada 2 konteks pertanyaan yang diajukan:
            - TRUE - Jika pengguna menyertakan NIM (Nomor Induk Mahasiswa).
            - FALSE - Jika pengguna tidak menyertakan nomor NIM (Nomor Induk Mahasiswa) dan tidak valid.
            Hasilkan hanya 1 sesuai kata (TRUE, FALSE).
        """

        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=state["question"]),
        ]
        response = chat_openai(messages).strip().lower()

        nim_match = re.search(r"\b(?:ktm|kartu tanda mahasiswa)\s*.*?(\b\d{10}\b)(?!\d)", state["question"], re.IGNORECASE)
        if nim_match:
            state["idNIMMhs"] = nim_match.group(1)
            response = True
        else:
            response = False
        is_complete = response == True

        state["checkKTM"] = is_complete
        print(f"Info KTM Lengkap? {is_complete}")
        return {"checkKTM": state["checkKTM"]}


    def incompleteInfoKTMAgent(state: AgentState):
        info = "\n--- Incomplete Info KTM ---"
        print(info)

        response = """
            Dari informasi yang ada, belum terdapat nomor NIM (Nomor Induk Mahasiswa) yang diberikan.
            NIM (Nomor Induk Mahasiswa) yang valid dari Undiksha berjumlah 10 digit angka.
            - Format penulisan pesan:
                KTM [NIM]
            - Contoh penulisan pesan:
                KTM XXXXXXXXXX
            Kirimkan NIM yang benar pada pesan ini sesuai format dan contoh, agar bisa mencetak Kartu Tanda Mahasiswa (KTM).
        """

        agent = "KTM_AGENT"
        answer = response

        agentOpinion = {
            "agent": agent,
            "answer": answer
        }

        # print(state["responseIncompleteNim"])
        return {"agentAnswer": [agentOpinion]}


    def infoKTMAgent(state: AgentState):
        info = "\n--- Info KTM ---"
        print(info)

        nim_match = re.search(r"\b(?:ktm|kartu tanda mahasiswa)\s*.*?(\b\d{10}\b)(?!\d)", state["question"], re.IGNORECASE)
        state["idNIMMhs"] = nim_match.group(1)
        id_nim_mhs = state.get("idNIMMhs", "ID NIM tidak berhasil didapatkan.")
        url_ktm_mhs = show_ktm_mhs(state)
        
        response = f"""
            Berikut informasi Kartu Tanda Mahasiswa (KTM) Anda.
            - NIM: {id_nim_mhs}
            - URL KTM: {url_ktm_mhs}
        """

        agent = "infoKTM_agent"
        answer = response

        agentOpinion = {
            "agent": agent,
            "answer": answer
        }

        # print(state["responseKTM"])
        return {"agentAnswer": [agentOpinion]}
    

    def routeToSpecificKTMAgent(state: AgentState):
        return state['checkKTM']