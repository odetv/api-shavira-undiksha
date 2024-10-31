def sort_answer_by_agent(active_agents: list, answers: list):
    print("Active agents: ", active_agents)
    print("Answers: ", answers)
    
    # Urutkan dan ambil hanya bagian answer
    sorted_answers = [resp['answer'] for resp in sorted(answers, key=lambda x: active_agents.index(x['agent']))]

    print(sorted_answers)

    return sorted_answers