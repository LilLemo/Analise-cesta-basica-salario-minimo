import google.generativeai as genai
import os
from dotenv import load_dotenv

# Carrega a sua chave de API do arquivo .env
load_dotenv()
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    print("Procurando modelos disponíveis para a sua chave...")

    # Lista todos os modelos que suportam o método 'generateContent'
    for model in genai.list_models():
      if 'generateContent' in model.supported_generation_methods:
        print(f" - Nome do Modelo: {model.name}")

    print("\nCopie um desses nomes de modelo (geralmente o que termina com 'pro') e cole no seu arquivo 'servidor_ia.py'.")

except Exception as e:
    print(f"Ocorreu um erro ao configurar ou listar os modelos: {e}")
    print("Verifique se sua chave de API no arquivo .env está correta.")