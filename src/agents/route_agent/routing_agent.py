from utils.agent_state import AgentState

def route_check_account(state: AgentState):
    return state["checkAccount"]

def route_info_ktm(state: AgentState):
    return state["checkKTM"]

def route_info_kelulusan(state: AgentState):
    return state["checkKelulusan"]