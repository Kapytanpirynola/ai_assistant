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



# ================================================================
#  🪙 CONFIGURACION DE MODELOS DE GEMINI Y OUTPUT TOKEN MANAGER 📈
# ================================================================
MODELS  = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

MAX_OUTPUT_TOKENS = 200


def create_chat(client, model):
    # Solo gemini-2.5 soporta ThinkingConfig
    if "2.5" in model:
        config = types.GenerateContentConfig(
            system_instruction="Me llamo Nyx, soy una IA asistente personal. Respondo de forma directa, eficiente y con ligero tono profesional.",
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            max_output_tokens=MAX_OUTPUT_TOKENS,
        )
    else:
        config = types.GenerateContentConfig(
            system_instruction="Me llamo Nyx, soy una IA asistente personal. Respondo de forma directa, eficiente y con ligero tono profesional.",
            max_output_tokens=MAX_OUTPUT_TOKENS,
        )

    return client.chats.create(model=model, config=config)

# ============================================================
# 🔐 FUNCIÓN DE CARGA SEGURA DE VARIABLES DE ENTORNO ⚙️
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
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig( 
            system_instruction="Me llamo Nyx, soy una IA asistente personal. Respondo de forma directa, eficiente y con ligero tono profesional.",
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            max_output_tokens=MAX_OUTPUT_TOKENS,
        ),
    )

    recorder = AudioToTextRecorder(model="tiny", language="es", spinner=False)  

    while True:
        try:
            print("You: ", end="", flush=True)
            user_input = recorder.text()
            print(user_input)
            if user_input.lower() == "exit": 
                break

            response = None
            for model in MODELS:
                try:
                    chat = create_chat(client, model)
                    response = chat.send_message_stream(user_input)
                    full_response = []
                    for chunk in response:
                        print(chunk.text, end="", flush=True)
                        full_response.append(chunk.text)
                    break  # ✅ si funcionó, salimos del for
                except Exception as e:
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        print(f"\n⚠️ {model} sin cuota, probando siguiente modelo...")
                        continue  # intenta el siguiente modelo
                    else:
                        raise  # si es otro error, lo sube al except exterior

            full_response_text = "".join(full_response).strip()
            print()
            if full_response_text:
                t = threading.Thread(target=speak, args=(full_response_text,))
                t.start()
                t.join()

        except KeyboardInterrupt:
            print("\n👋 Cerrando Nyx...")
            break
        except Exception as e:
            print(f"\n⚠️ Error: {e}")
            print("🔄 Continuando...")
            continue

if __name__ == "__main__":
    main()
