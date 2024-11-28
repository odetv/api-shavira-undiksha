from langchain_core.messages import SystemMessage
from utils.agent_state import AgentState
from utils.llm import chat_llm
from utils.debug_time import time_check


@time_check
def resultWriterAgent(state: AgentState):
    print(f"Debug: Total agents di result writer: {state['totalAgents']}")
    print(f"Debug: Agents active di result writer: {len(state['finishedAgents'])}")

    if len(state["finishedAgents"]) < state["totalAgents"]:
        print("Menunggu agen lain untuk menyelesaikan...")
        return None
    
    elif len(state["finishedAgents"]) == state["totalAgents"]:
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