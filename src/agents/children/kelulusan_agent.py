import re
from src.models import AgentState
from utils.api_undiksha import show_kelulusan_pmb
from utils.llm import chat_openai, chat_ollama, chat_groq
from langchain_core.messages import HumanMessage, SystemMessage


class KelulusanAgent:
    def kelulusanAgent(state: AgentState):
        info = "\n--- CEK KELULUSAN SMBJM ---"
        print(info)

        prompt = """
            Anda adalah seoarang analis informasi kelulusan SMBJM.
            Tugas Anda adalah mengklasifikasikan jenis pertanyaan pada konteks Undiksha (Universitas Pendidikan Ganesha).
            Sekarang tergantung pada jawaban Anda, akan mengarahkan ke agent yang tepat.
            Ada 2 konteks pertanyaan yang diajukan:
            - TRUE - Jika pengguna menyertakan Nomor Pendaftaran (Format 10 digit angka) dan Tanggal Lahir (Format YYYY-MM-DD).
            - FALSE - Jika pengguna tidak menyertakan Nomor Pendaftaran (Format 10 digit angka) dan Tanggal Lahir (Format YYYY-MM-DD).
            Hasilkan hanya 1 sesuai kata (TRUE, FALSE).
        """
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=state["question"]),
        ]
        response = chat_openai(messages).strip().lower()

        noPendaftaran_match = re.search(r"\b(?:nmr|no|nomor|nmr.|no.|nomor.|nmr. |no. |nomor. )\s*pendaftaran.*?(\b\d{10}\b)(?!\d)", state["question"], re.IGNORECASE)
        tglLahirPendaftar_match = re.search(r"(?:ttl|tanggal lahir|tgl lahir|lahir|tanggal-lahir|tgl-lahir|lhr|tahun|tahun lahir|thn lahir|thn|th lahir)[^\d]*(\d{4}-\d{2}-\d{2})", state["question"], re.IGNORECASE)

        print(noPendaftaran_match)
        print(tglLahirPendaftar_match)

        if noPendaftaran_match and tglLahirPendaftar_match:
            state["noPendaftaran"] = noPendaftaran_match.group(1)
            state["tglLahirPendaftar"] = tglLahirPendaftar_match.group(1)
            response = "true"
        else:
            response = "false"
        is_complete = response == "true"

        state["checkKelulusan"] = is_complete
        print(f"Info Kelulusan Lengkap? {is_complete}")
        return {"checkKelulusan": state["checkKelulusan"]}


    def incompleteInfoKelulusanAgent(state: AgentState):
        info = "\n--- Incomplete Info Kelulusan SMBJM ---"
        print(info)

        response = """
            Dari informasi yang ada, belum terdapat Nomor Pendaftaran dan Tanggal Lahir Pendaftar SMBJM yang diberikan.
            - Format penulisan pesan:
                Nomor Pendaftaran [NO_PENDAFTARAN_10_DIGIT]
                Tanggal Lahir [YYYY-MM-DD]
            - Contoh penulisan pesan:
                Nomor Pendaftaran 3201928428
                Tanggal Lahir 2005-01-30
            Kirimkan dengan benar pada pesan ini sesuai format dan contoh, agar bisa mengecek kelulusan SMBJM Undiksha.
        """
        agent = "KELULUSAN_AGENT"
        answer = response

        agentOpinion = {
            "agent": agent,
            "answer": answer
        }

        # print(state["responseIncompleteInfoKelulusan"])
        return {"agentAnswer": [agentOpinion]}


    def infoKelulusanAgent(state: AgentState):
        info = "\n--- Info Kelulusan SMBJM ---"
        print(info)

        noPendaftaran_match = re.search(r"\b(?:nmr|no|nomor|nmr.|no.|nomor.|nmr. |no. |nomor. )\s*pendaftaran.*?(\b\d{10}\b)(?!\d)", state["question"], re.IGNORECASE)
        tglLahirPendaftar_match = re.search(r"(?:ttl|tanggal lahir|tgl lahir|lahir|tanggal-lahir|tgl-lahir|lhr|tahun|tahun lahir|thn lahir|thn|th lahir)[^\d]*(\d{4}-\d{2}-\d{2})", state["question"], re.IGNORECASE)
        state["noPendaftaran"] = noPendaftaran_match.group(1)
        state["tglLahirPendaftar"] = tglLahirPendaftar_match.group(1)

        try:
            kelulusan_info = show_kelulusan_pmb(state)
            no_pendaftaran = kelulusan_info.get("nomor_pendaftaran", "")
            nama_siswa = kelulusan_info.get("nama_siswa", "")
            tgl_lahir = kelulusan_info.get("tgl_lahir", "")
            tgl_daftar = kelulusan_info.get("tahun", "")
            pilihan_prodi = kelulusan_info.get("program_studi", "")
            status_kelulusan = kelulusan_info.get("status_kelulusan", "")

        except Exception as e:
            # print("Error retrieving graduation information:", e)
            return {
                "agentAnswer": [{
                    "answer": "Terjadi kesalahan dalam mendapatkan informasi kelulusan. Silakan coba lagi nanti."
                }]
            }

        response = f"""
            Berikut informasi Kelulusan Peserta SMBJM di Undiksha (Universitas Pendidikan Ganesha).
            - Nomor Pendaftaran: {no_pendaftaran}
            - Nama Siswa: {nama_siswa}
            - Tanggal Lahir: {tgl_lahir}
            - Tahun Daftar: {tgl_daftar}
            - Pilihan Program Studi: {pilihan_prodi}
            - Status Kelulusan: {status_kelulusan}
            Berdasarkan informasi, berikan ucapan selamat bergabung di menjadi bagian dari Universitas Pendidikan Ganesha jika {nama_siswa} lulus, atau berikan motivasi {nama_siswa} jika tidak lulus.
        """

        agent = "KELULUSAN_AGENT"
        answer = response

        agentOpinion = {
            "agent": agent,
            "answer": answer
        }
        
        # print(state["responseKelulusan"])
        return {"agentAnswer": [agentOpinion]}
    
    def routeToSpecificKelulusanAgent(state: AgentState):
        return state['checkKelulusan']