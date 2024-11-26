from langchain_core.messages import SystemMessage
from utils.agent_state import AgentState
from utils.llm import chat_llm
from utils.debug_time import time_check


@time_check
def resultWriterAgent(state: AgentState):
    print(f"Debug: Total agents di result writer: {state['totalAgents']}")
    print(f"Debug: Agents active di result writer: {state['activeAgents']}")

    expected_agents_count = len(state["finishedAgents"])
    total_agents = 0
    if "general_agent" in state["finishedAgents"]:
        total_agents += 1
    if "graderDocs_agent" in state["finishedAgents"]:
        total_agents += 1
    if "answerGeneral_agent" in state["finishedAgents"]:
        total_agents += 1
    if "news_agent" in state["finishedAgents"]:
        total_agents += 1
    if "account_agent" in state["finishedAgents"]:
        total_agents += 1
    if "resetAccount_agent" in state["finishedAgents"]:
        total_agents += 1
    if "incompleteAccount_agent" in state["finishedAgents"]:
        total_agents += 1
    if "anomalyAccount_agent" in state["finishedAgents"]:
        total_agents += 1
    if "kelulusan_agent" in state["finishedAgents"]:
        total_agents += 1
    if "incompleteInfoKelulusan_agent" in state["finishedAgents"]:
        total_agents += 1
    if "infoKelulusan_agent" in state["finishedAgents"]:
        total_agents += 1
    if "ktm_agent" in state["finishedAgents"]:
        total_agents += 1
    if "incompleteInfoKTM_agent" in state["finishedAgents"]:
        total_agents += 1
    if "infoKTM_agent" in state["finishedAgents"]:
        total_agents += 1
    print(f"DEBUG: finishedAgents = {state['finishedAgents']}")
    print(f"DEBUG: expected_agents_count = {expected_agents_count}, total_agents = {total_agents}")

    if expected_agents_count < total_agents:
        print("Menunggu agen lain untuk menyelesaikan...")
        return None
    
    info = "\n--- RESULT WRITER ---"
    print(info)

    prompt = f"""
        Berikut pedoman yang harus diikuti untuk menulis ulang informasi:
        - Awali dengan "Salam Harmoni🙏"
        - Berikan informasi secara lengkap dan jelas apa adanya sesuai informasi yang diberikan.
        - Jangan tawarkan informasi lainnya selain konteks yang didapat saja.
        - Hasilkan response dalam format Markdown.
        Berikut adalah informasinya:
        {state["answerAgents"]}
    """

    messages = [
        SystemMessage(content=prompt)
    ]
    response = chat_llm(messages)

    state["responseFinal"] = response
    return {"responseFinal": state["responseFinal"]}