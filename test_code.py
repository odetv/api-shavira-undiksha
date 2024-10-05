from typing import Dict, List, Any
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import Graph, END
import asyncio
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv('OPENAI_API')
# Inisialisasi LLM
llm = OpenAI(api_key=openai_api_key)

# Agen Analyzer yang menggunakan LLM untuk menganalisis input
class AnalyzerAgent:
    def __init__(self):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """Anda adalah sistem analisis yang menentukan tindakan yang diperlukan.
            Berdasarkan input yang diberikan, pilih opsi yang sesuai: A, B, atau C.
            - A: Jika input membutuhkan analisis sederhana
            - B: Jika input membutuhkan penelitian mendalam
            - C: Jika input membutuhkan verifikasi fakta
            Berikan jawaban dalam format satu huruf saja: A atau B atau C"""),
            ("user", "{input_text}")
        ])
        self.llm = llm
    
    async def analyze(self, input_text: str) -> str:
        chain = self.prompt | self.llm
        result = await chain.ainvoke({"input_text": input_text})
        return result.content.strip().upper()

# Agen-agen pelaksana
class AgentA:
    async def run(self, state: Dict[str, Any]) -> str:
        print("Agent A: Melakukan analisis sederhana...")
        await asyncio.sleep(2)
        return "Hasil analisis sederhana selesai"

class AgentB:
    async def run(self, state: Dict[str, Any]) -> str:
        print("Agent B: Melakukan penelitian mendalam...")
        await asyncio.sleep(3)
        return "Hasil penelitian mendalam selesai"

class AgentC:
    async def run(self, state: Dict[str, Any]) -> str:
        print("Agent C: Melakukan verifikasi fakta...")
        await asyncio.sleep(2.5)
        return "Hasil verifikasi fakta selesai"

# Fungsi untuk menentukan dan menjalankan agen
async def execute_agents(state: Dict[str, Any]) -> Dict[str, Any]:
    analyzer = AnalyzerAgent()
    required_actions = await analyzer.analyze(state["input_text"])
    print(f"Analyzer memutuskan untuk menjalankan: {required_actions}")
    
    # Inisialisasi agen-agen
    agents = {
        'A': AgentA(),
        'B': AgentB(),
        'C': AgentC()
    }
    
    tasks = []
    results = {}
    
    if 'A' in required_actions:
        tasks.append(('A', agents['A'].run(state)))
    if 'B' in required_actions:
        tasks.append(('B', agents['B'].run(state)))
    if 'C' in required_actions:
        tasks.append(('C', agents['C'].run(state)))
    
    # Jalankan agen-agen yang diperlukan secara paralel
    if tasks:
        task_results = await asyncio.gather(*(task[1] for task in tasks))
        for (agent_id, _), result in zip(tasks, task_results):
            results[f"agent_{agent_id}_result"] = result
    
    return {
        "analysis_result": required_actions,
        **results
    }

# Buat workflow
def create_workflow():
    workflow = Graph()
    
    # Tambahkan node untuk eksekusi agen
    workflow.add_node("execute_agents", execute_agents)
    
    # Definisikan alur kerja
    workflow.set_entry_point("execute_agents")
    workflow.add_edge("execute_agents", END)
    
    return workflow.compile()

# Fungsi utama untuk menjalankan workflow
async def main():
    # Contoh input yang berbeda untuk menguji berbagai skenario
    test_inputs = [
        "Apakah benar bahwa bumi itu bulat? Tolong cek faktanya.",  # Mungkin menghasilkan C
        "Bagaimana dampak perubahan iklim terhadap biodiversitas?",  # Mungkin menghasilkan B dan C
        "Berapa 2 + 2?"  # Mungkin menghasilkan A
    ]
    
    workflow = create_workflow()
    
    for input_text in test_inputs:
        print("\n=== Memulai Proses Baru ===")
        print(f"Input: {input_text}")
        
        initial_state = {
            "input_text": input_text
        }
        
        result = await workflow.ainvoke(initial_state)
        
        print("\nHasil:")
        for key, value in result.items():
            print(f"{key}: {value}")
        print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())