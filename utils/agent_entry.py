from utils.agent_state import AgentState
from typing_extensions import List


def agentEntry(state: AgentState, agent_name: str, new_child_agents: List[str]) -> None:
    if "activeAgents" not in state:
        state["activeAgents"] = []

    new_child_agents_set = set(new_child_agents)

    for agent in state["activeAgents"]:
        if agent["agent_active"] == agent_name:
            agent["child_agents"] = list(set(agent["child_agents"]) | new_child_agents_set)
            break
    else:
        state["activeAgents"].append({
            "agent_active": agent_name,
            "child_agents": list(new_child_agents_set)
        })

    seen = set()
    state["activeAgents"] = [
        agent for agent in state["activeAgents"]
        if agent["agent_active"] not in seen and not seen.add(agent["agent_active"])
    ]

    print("DEBUG AGENT ACTIVE:::", state["activeAgents"])
    
    total_length = sum(1 + len(agent["child_agents"]) for agent in state["activeAgents"])
    print("DEBUG PANJANG AGENT:::", total_length)
