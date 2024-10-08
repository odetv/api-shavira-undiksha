from llm import chat_openai
import re


question = "hai, bagaimana cara reset password akun google sudiartika@undiksha.ac.id?"

prompt = f"""
        Pertanyaan : {question}
        anda adalah agen bertugas menjawab pertanyaan,:
        - Apa email yang akan direset passwordnya, jika tidak disebutkan emailnya maka null,
        - Apa jenis email yang akan direset passwordnya, jawablah sesuai pilihan dibawah:
            - "GOOGLE_EMAIL" (ketika user menyebutkan jelas bahwa akan mereset akun google, jika user hanya menyebutkan akun nya tanpa jelas memberikan pernyataan bahwa akan mereset akun GOOGLE maka alihkan ke INCOMPLETE_INFORMATION), 
            - "SSO_EMAIL" (ketika dari pernyataan user jelas menyebutkan reset password untuk SSO Undiksha atau E-Ganesha), 
            - "HYBRID_EMAIL" (ketika dari pernyataan user jelas menyebutkan reset password untuk akun google undiksha dan SSO E-Ganesha), 
            - "INCOMPLETE_INFORMATION" (ketika dari pernyataan user tidak menyebutkan apakah reset password untuk akun google undiksha atau SSO E-Ganesha)
        - Apa status login dari pertanyaan diatas, jawablah sesuai pilihan dibawah:
            - "TRUE" (Ketika user secara jelas bahwa akun undikshanya sudah diloginkan di perangkat baik hp/laptop/komputer),
            - "FALSE" (Ketika user secara jelas bahwa akun undikshanya belum diloginkan di perangkat baik hp/laptop/komputer)
            - "NO_INFO" (Ketika user tidak jelas apakah akun undikshanya sudah diloginkan di perangkat baik hp/laptop/komputer atau belum)
        jawab pertanyaan diatas, dengan jawaban dipisah dengan tanda koma, hasilkan hanya jawabannya saja
    """

response = chat_openai(question=prompt, model='gpt-4o-mini')

result = [item.strip() for item in response.split(",")]

print(result)