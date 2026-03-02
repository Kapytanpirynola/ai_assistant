from google import genai    # Imports the main Gemini AI library
from google.genai import types        # Imports data types for configuring requests
import os                             # Imports the 'os' module for system interactions
from dotenv import load_dotenv   
from RealtimeSTT import AudioToTextRecorder  # Imports a custom module for real-time speech-to-text recording  

# Load environment variables from .env file
def main():
    load_dotenv()

    # Get the API key from the environment variables
    api_key = os.getenv("GEMINI_API_KEY")

    client = genai.Client(api_key=api_key)  # Creates a client instance for the Gemini API

    # Check if the key was loaded successfully
    if not api_key:                
        raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")

    print("Validando api key...")
    print("API key válida. Iniciando chat...")
    print("Hola soy tu asistente de IA. ¿En qué puedo ayudarte hoy? (Escribe 'exit' para salir)");



    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig( 
            system_instruction=" ",
            thinking_config=types.ThinkingConfig(thinking_budget=0) 
        ),
    )

    recorder = AudioToTextRecorder(model="tiny", language="es")       # Creates an instance of the audio recorder for real-time speech-to-text conversion


    while True:
        print("You: ", end="", flush=True)  # Prompts the user for input
        user_input = recorder.text() 
        print(user_input)
        if user_input.lower() == "exit": 
            break

        response = chat.send_message_stream(user_input)
        for chunk in response:
            print(chunk.text, end="", flush=True)
        print() 

if __name__ == "__main__":
    main()