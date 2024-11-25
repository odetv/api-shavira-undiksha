import re
from langchain_core.messages import HumanMessage, SystemMessage
from utils.agent_state import AgentState
from utils.llm import chat_llm
from utils.debug_time import time_check


@time_check
def accountAgent(state: AgentState):
    info = "\n--- ACCOUNT ---"
    print(info)

    prompt = """
        Anda adalah seorang admin dari sistem akun Undiksha (Universitas Pendidikan Ganesha).
        Tugas Anda adalah mengklasifikasikan jenis pertanyaan.
        Sekarang tergantung pada jawaban Anda, akan mengarahkan ke agent yang tepat.
        Ada 3 konteks pertanyaan yang diajukan:
        - RESET - Hanya jika terdapat email dengan domain "@undiksha.ac.id" atau "@student.undiksha.ac.id" dan sudah terdapat informasi mengenai status sudah login di email/gmail/google/hp/laptop/komputer (email dan status wajib disertakan, jika salah satu tidak disebutkan berarti incomplete).
        - INCOMPLETE - Hanya jika tidak terdapat email dengan domain "@undiksha.ac.id" atau "@student.undiksha.ac.id", atau tidak terdapat informasi mengenai status sudah login di email/gmail/google/hp/laptop/komputer (email dan status wajib disertakan), atau hanya jika ingin reset atau ubah password.
        - ANOMALY - Hanya jika lupa email, tidak mengetahui status login dengan jelas, atau lupa akun Google nya.
        Hati-hati dengan domain email yang serupa atau mirip, pastikan benar-benar sesuai.
        Hasilkan hanya 1 kata yang paling sesuai (RESET, INCOMPLETE, ANOMALY).
    """
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=state["accountQuestion"]),
    ]
    response = chat_llm(messages).strip().lower()
    state["checkAccount"] = response
    state["finishedAgents"].add("account_agent") 
    print(f"Info Account Lengkap? {response}")

    promptParsingAccount = """
        Anda adalah seoarang pemecah isi pertanyaan pengguna.
        Tugas Anda sangat penting. Klasifikasikan atau parsing pertanyaan dari pengguna untuk dimasukkan ke variabel sesuai konteks.
        Ada 2 konteks penting dalam pertanyaan dari pengguna untuk dimasukkan ke variabel:
        - emailAccountUser - Masukkan hanya jika terdapat email dengan domain "@undiksha.ac.id" atau "@student.undiksha.ac.id", jika email tidak sesuai maka masukkan "null".
        - loginAccountStatus - Jika ada informasi status sudah login di email/gmail/google/hp/laptop/komputer maka masukkan "true", jika tidak ada kejelasan maka masukkan "false".
        Hati-hati dengan domain email yang serupa atau mirip, pastikan benar-benar sesuai.
        Jawab sesuai dengan kategori dengan contoh seperti ({"emailAccountUser": "email valid", "loginAccountStatus": "true atau false"}).
        Buat dengan format data JSON tanpa membuat key baru.
    """
    messagesParsingAccount = [
        SystemMessage(content=promptParsingAccount),
        HumanMessage(content=state["accountQuestion"]),
    ]
    responseParsingAccount = chat_llm(messagesParsingAccount).strip().lower()

    json_like_data = re.search(r'\{.*\}', responseParsingAccount, re.DOTALL)
    if json_like_data:
        cleaned_response = json_like_data.group(0)
        print(f"DEBUG: Bagian JSON-like yang diambil: {cleaned_response}")
    else:
        print("DEBUG: Tidak ditemukan data JSON-like.")
        cleaned_response = ""
    emailAccountUser_match = re.search(r'"emailaccountuser"\s*:\s*"([^"]*)"', cleaned_response)
    loginAccountStatus_match = re.search(r'"loginaccountstatus"\s*:\s*"([^"]*)"', cleaned_response)
    state["emailAccountUser"] = emailAccountUser_match.group(1) if emailAccountUser_match and emailAccountUser_match.group(1) else "Tidak ada informasi"
    state["loginAccountStatus"] = loginAccountStatus_match.group(1) if loginAccountStatus_match and loginAccountStatus_match.group(1) else "Tidak ada informasi"
    print(f"Debug: State 'emailAccountUser' setelah update: {state['emailAccountUser']}")
    print(f"Debug: State 'loginAccountStatus' setelah update: {state['loginAccountStatus']}")
    
    return state