from src.agents import QuestionIdentifierAgent

initial_state = QuestionIdentifierAgent.questionIdentifierAgent({"question": "resetkan password saya"})
context = initial_state["initiated_agents"].keys()

print(len(context))