from google import genai                        
from google.genai import types                  
import os                                       
from dotenv import load_dotenv   
from RealtimeSTT import AudioToTextRecorder     
import torch
import pyttsx3
import threading
from cryptography.fernet import Fernet
import tempfile


MAX_OUTPUT_TOKENS = 200

# ============================================================
# 🔐 FUNCIÓN DE CARGA SEGURA DE VARIABLES DE ENTORNO
# ============================================================

def load_encrypted_env():
    try:
        # Ruta del escritorio — igual que en tu encrypt_env.py
        with open(r"C:\Users\adria\Escritorio\.env.key", "rb") as f:
            key = f.read()

        fernet = Fernet(key)

        with open(".env.encrypted", "rb") as f:
            encrypted_data = f.read()

        decrypted_data = fernet.decrypt(encrypted_data)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".env", mode="wb") as tmp:
            tmp.write(decrypted_data)
            tmp_path = tmp.name

        load_dotenv(tmp_path)
        os.unlink(tmp_path)
        print("🔐 Variables cargadas de forma segura.")

    except FileNotFoundError as e:
        print(f"⚠️  Archivo no encontrado: {e}")
        print("⚠️  Usando .env normal como fallback...")
        load_dotenv()


def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 175)
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()
    engine.stop()
    
def main():
    load_encrypted_env()

    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not gemini_api_key:                
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    print("API KEY IS FINEEEE...")

    client = genai.Client(api_key=gemini_api_key)

    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig( 
            system_instruction="Me llamo Nyx, soy una IA asistente personal. Respondo de forma directa, eficiente y con ligero tono profesional.",
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            max_output_tokens=MAX_OUTPUT_TOKENS,
        ),
    )

    recorder = AudioToTextRecorder(model="tiny", language="es", spinner=False)  

    while True:
        print("You: ", end="", flush=True)
        user_input = recorder.text()
        print(user_input)
        if user_input.lower() == "exit": 
            break

        response = chat.send_message_stream(user_input)
        full_response = []

        for chunk in response:
            print(chunk.text, end="", flush=True)
            full_response.append(chunk.text)
        
        full_response_text = "".join(full_response).strip()
        print()
        if full_response_text:
            t = threading.Thread(target=speak, args=(full_response_text,))
            t.start()
            t.join()

    recorder.shutdown()
if __name__ == "__main__":
    main()
