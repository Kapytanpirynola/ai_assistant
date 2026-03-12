from google import genai                        
from google.genai import types                  
import os                                       
from dotenv import load_dotenv   
from RealtimeSTT import AudioToTextRecorder     
import torch
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
from cryptography.fernet import Fernet          # ← NUEVO: librería de encriptación
import tempfile                                 # ← NUEVO: para archivos temporales seguros

MAX_OUTPUT_TOKENS = 100

# ============================================================
# 🔐 FUNCIÓN DE CARGA SEGURA DE VARIABLES DE ENTORNO
# ============================================================
# ¿QUÉ HACE?
# En lugar de leer el .env en texto plano, lee el .env.encrypted
# (que es ilegible sin la clave), lo desencripta en memoria,
# lo guarda MUY brevemente en un archivo temporal, carga las
# variables, y borra el temporal de inmediato.
#
# ANALOGÍA:
# Imagina que tus API keys están en una caja fuerte (.env.encrypted).
# La llave de la caja fuerte es .env.key.
# Abres la caja, tomas lo que necesitas, y la cierras al instante.
# Nadie que vea tu carpeta puede leer tus keys sin la llave.
# ============================================================

def load_encrypted_env():
    try:
        # PASO 1: Leer la llave de encriptación desde .env.key
        # .env.key contiene una clave Fernet de 32 bytes en base64
        # Ejemplo de cómo se ve: b'abc123XYZ...' (44 caracteres)
        with open(r"C:\Users\adria\Escritorio\.env.key", "rb") as f:
            key = f.read()

        # PASO 2: Crear el objeto desencriptador con esa llave
        # Fernet es un sistema de encriptación SIMÉTRICA:
        # → La misma llave que encriptó, desencripta
        # → Si no tienes la llave exacta, es imposible leer el archivo
        fernet = Fernet(key)

        # PASO 3: Leer el archivo encriptado (.env.encrypted)
        # Este archivo se ve así en disco: gAAAAABl... (texto ilegible)
        # SIN la llave, no puedes saber qué contiene
        with open(".env.encrypted", "rb") as f:
            encrypted_data = f.read()

        # PASO 4: Desencriptar → obtenemos el .env original en memoria
        # decrypted_data es bytes con el contenido:
        # GEMINI_API_KEY=AIza...
        # ELEVENLABS_API_KEY=sk_...
        # Esto NUNCA se escribe en disco como texto plano
        decrypted_data = fernet.decrypt(encrypted_data)

        # PASO 5: Guardar MUY brevemente en archivo temporal
        # ¿Por qué temporal? Porque load_dotenv() necesita un archivo.
        # Lo creamos, cargamos las variables, y lo borramos al instante.
        # El archivo temporal se crea en la carpeta temp del sistema
        # operativo (C:\Users\adria\AppData\Local\Temp en Windows)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".env", mode="wb") as tmp:
            tmp.write(decrypted_data)
            tmp_path = tmp.name  # Guardamos la ruta para borrarlo luego

        # PASO 6: Cargar las variables del archivo temporal al entorno
        # Después de esto, os.getenv("GEMINI_API_KEY") funciona normal
        load_dotenv(tmp_path)

        # PASO 7: Borrar el archivo temporal INMEDIATAMENTE
        # Ya no necesitamos el archivo, las variables están en memoria
        # os.unlink() es el equivalente a borrar un archivo
        os.unlink(tmp_path)

        print("🔐 Variables cargadas de forma segura.")

    except FileNotFoundError as e:
        # Si no encuentra .env.encrypted o .env.key, cae al .env normal
        # Útil durante desarrollo antes de encriptar
        print(f"⚠️  Archivo no encontrado: {e}")
        print("⚠️  Usando .env normal como fallback...")
        load_dotenv()


# ============================================================
# ¿QUÉ ARCHIVOS EXISTEN EN TU PROYECTO DESPUÉS DE ENCRIPTAR?
#
#  .env.key         → La LLAVE (guárdala fuera del proyecto)
#  .env.encrypted   → El cofre (puedes subirlo a GitHub, es ilegible)
#  .env             → BORRAR después de encriptar
#
# FLUJO DE SEGURIDAD:
#  Antes: .env (texto plano) → cualquiera que vea tu repo ve tus keys
#  Después: .env.encrypted → sin .env.key es basura ilegible
# ============================================================

def main():
    load_encrypted_env()  # ← Reemplaza el load_dotenv() original

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")

    if not gemini_api_key:                
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    if not elevenlabs_api_key:
        raise ValueError("ELEVENLABS_API_KEY environment variable not set.")

    print("API KEY IS FINEEEE...")

    client = genai.Client(api_key=gemini_api_key)

    elevenlabs = ElevenLabs(
        api_key=elevenlabs_api_key,
    )

    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig( 
            system_instruction="Me llamo Nyx, soy un modelo de lenguaje desarrollado por Google",
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
            audio = elevenlabs.text_to_speech.convert(
                text=full_response_text,
                voice_id="21m00Tcm4TlvDq8ikWAM",
                model_id="eleven_turbo_v2_5",
                output_format="mp3_44100_128",
            )
            play(audio)

    recorder.shutdown()

if __name__ == "__main__":
    main()