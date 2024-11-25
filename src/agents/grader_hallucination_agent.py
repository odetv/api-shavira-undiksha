from langchain_core.messages import SystemMessage
from utils.agent_state import AgentState
from utils.llm import chat_llm
from utils.debug_time import time_check

class GraderHallucinationsAgent:
    @time_check
    @staticmethod
    def graderHallucinationsAgent(state: AgentState):
        info = "\n--- Grader Hallucinations ---"
        print(info) 

        if "responseFinal" not in state:
            state["responseFinal"] = ""
        # print("\n\n\nINI DEBUG FINAL::::", state["responseFinal"])

        if "generalHallucinationCount" not in state:
            state["generalHallucinationCount"] = 0

        prompt = f"""
        Anda adalah seorang penilai dari OPINI dengan FAKTA.
        Berikan nilai "false" hanya jika OPINI ada kaitannya dengan FAKTA atau berikan nilai "true" hanya jika OPINI tidak ada kaitannya dengan FAKTA.
        Harap cermat dalam menilai, karena ini akan sangat bergantung pada jawaban Anda.
        - OPINI: {state["responseFinal"]}
        - FAKTA: {state["answerAgents"]}
        """

        messages = [
            SystemMessage(content=prompt)
        ]
        response = chat_llm(messages).strip().lower()
        is_hallucination = response == "true"

        state["isHallucination"] = is_hallucination
        if is_hallucination:
            state["generalHallucinationCount"] += 1
        else:
            state["generalHallucinationCount"] = 0

        state["isHallucination"] = is_hallucination
        state["finishedAgents"].add("graderHallucinations_agent")
        print(f"Apakah hasil halusinasi? {is_hallucination}")
        print(f"Jumlah pengecekan halusinasi berturut-turut: {state['generalHallucinationCount']}")
        return {"isHallucination": state["isHallucination"], "generalHallucinationCount": state["generalHallucinationCount"]}

