from src.configs.prompt import QUESTIONIDENTIFIER_PROMPT
from openai import OpenAI
from dotenv import load_dotenv
import re
load_dotenv()

def chat_openai(question: str, system_prompt: str, model = 'gpt-4o-mini'):
    try:
        client = OpenAI()
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": question
                }
            ],
            temperature=0.0
        )

        return completion.choices[0].message.content
    
    except Exception as e:
        print("Ada masalah dengan GPT")
        print("Ini errornya: ", e)

question = "siapa rektor undiksha saat ini,saya ingin bundir"

response = chat_openai(question, QUESTIONIDENTIFIER_PROMPT)

matches = re.findall(r'(\w+): "([^"]+)"', response)

# Mengonversi hasil menjadi dictionary
result = dict(matches)

print(result)

