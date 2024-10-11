def sort_answer_by_agent(active_agents: list, answers: list):
    sorted_answers = sorted(
        answers,
        key=lambda x: active_agents.index(x['agent'].lower()) if x['agent'].lower() in active_agents else len(active_agents))

    answers_list = [answer['answer'] for answer in sorted_answers]

    return answers_list