import os
import json
import re 
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai import errors 
import pyttsx3 
import speech_recognition as sr 

# --- Import ALL System Tools ---
from tools import (
    create_file, 
    create_directory, 
    execute_command, 
    list_current_directory_contents, 
    open_application_or_url,
    lookup_phone_number_info,             
    scan_system_for_executables,
    assign_keyboard_shortcut,
    send_web_message # NEW: Web messaging tool added and imported
)

# --- Configuration & Setup ---

DISCOVERED_APPS_FILE = "discovered_apps.json"
API_DELAY_SECONDS = 3
MODEL_NAME = 'gemini-2.5-flash'

load_dotenv()

# API Key Loading and Management
API_KEYS = [
    os.getenv("GEMINI_API_KEY_0"),
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3"),
    os.getenv("GEMINI_API_KEY_4"),
]
VALID_API_KEYS = [key for key in API_KEYS if key]
if not VALID_API_KEYS:
    print("FATAL: At least one valid GEMINI_API_KEY_N not found in .env file.")
    exit()

# Global state for API management
current_api_key_index = 0
client = None 
chat = None

# --- GLOBAL AVAILABLE TOOLS LIST ---
# This variable was previously defined inside run_assistant, causing issues.
# It is now defined globally and includes the new web messaging tool.
AVAILABLE_TOOLS = [
    create_file, 
    create_directory, 
    execute_command, 
    list_current_directory_contents,
    open_application_or_url,
    lookup_phone_number_info,
    scan_system_for_executables,
    assign_keyboard_shortcut,
    send_web_message # <-- NEW TOOL IS NOW REGISTERED HERE
]
# --- END GLOBAL AVAILABLE TOOLS LIST ---


# --- API Client Initialization Function ---
def initialize_client_and_chat(system_instruction, tools=AVAILABLE_TOOLS): # tools=AVAILABLE_TOOLS default argument added
    global current_api_key_index, client, chat
    
    if current_api_key_index >= len(VALID_API_KEYS):
        print("FATAL: All available API keys have failed.")
        return False
    
    key = VALID_API_KEYS[current_api_key_index]
    
    try:
        client = genai.Client(api_key=key)
        
        # Chat session is initialized with the global AVAILABLE_TOOLS
        chat = client.chats.create(
            model=MODEL_NAME,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=tools
            )
        )
        print(f"INFO: Successfully initialized with API Key Index {current_api_key_index + 1}.")
        return True
        
    except Exception as e:
        print(f"ERROR: API Key Index {current_api_key_index + 1} failed during initialization: {e}")
        current_api_key_index += 1
        # Try initializing with the next key recursively
        return initialize_client_and_chat(system_instruction, tools)

# --- Helper Functions ---
def load_dynamic_app_tools() -> list:
    """Load discovered app names from JSON file for System Instruction."""
    if not os.path.exists(DISCOVERED_APPS_FILE):
        return []
    try:
        with open(DISCOVERED_APPS_FILE, 'r') as f:
            discovered_apps = json.load(f)
        return list(discovered_apps.keys())
    except Exception as e:
        return []

# --- Main Conversational Loop ---
def run_assistant():
    """The main function to run the conversational AI assistant."""
    global current_api_key_index, client, chat
    
    # ... (TTS/STT setup code) ...
    tts_engine = pyttsx3.init()
    tts_engine.setProperty('rate', 150)  
    voice_mode_enabled = False 
    r = sr.Recognizer()

    def speak(text):
        filtered_text = re.sub(r'[^\w\s,\.\?\!]', '', text).replace('*', '') 
        print(f"Assistant: {text}") 
        tts_engine.say(filtered_text)
        tts_engine.runAndWait()
    # ... (End TTS/STT setup) ...

    speak("Hello Eisa, your assistant is starting up.")
    
    discovered_app_names = load_dynamic_app_tools()
    
    # SYSTEM_INSTRUCTION_TEXT remains the same
    SYSTEM_INSTRUCTION_TEXT = (
        "You are an expert system automation assistant. Your goal is to help the user control "
        "their local system (file creation, running commands, opening apps/sites, etc.) by using the provided tools. "
        "The user speaks Hindi but types in English. You must also reply in Hindi, typed in English. "
        "ALWAYS use the tools when the user asks for a system action. "
        "If multiple tools need to be called, prioritize the most relevant one first. "
        "Do not perform the action yourself; always respond with the function call."
        f"\n[HINT: The following common apps were previously discovered: {', '.join(discovered_app_names)}. Use open_application_or_url for these.]"
        # HINT: send_web_message tool is available for whatsapp and telegram web automation.
    )

    # Initialize client and chat with the first working key
    if not initialize_client_and_chat(SYSTEM_INSTRUCTION_TEXT): # tools argument is no longer needed here
        speak("Fatal error: Could not initialize the assistant with any provided API key. Shutting down.")
        return 
    
    speak(f"Assistant is running in keyboard mode using Key {current_api_key_index + 1}. Type 'enable voice assistant' to start listening.")

    while True:
        user_input = ""
        
        # ... (Input Handling: Voice/Keyboard logic remains the same) ...
        if voice_mode_enabled:
            # VOICE INPUT MODE
            with sr.Microphone() as source:
                print("\nListening... (Say 'deactivate' or 'exit')")
                r.pause_threshold = 0.8
                try:
                    r.adjust_for_ambient_noise(source)
                    audio = r.listen(source, timeout=5, phrase_time_limit=10)
                    user_input = r.recognize_google(audio, language='en-IN') 
                    print(f"You said: {user_input}")
                except sr.WaitTimeoutError:
                    continue 
                except sr.UnknownValueError:
                    speak("Sorry, I could not understand the audio. Please try again.")
                    continue
                except sr.RequestError:
                    speak("Speech service is currently unavailable. Please check your internet connection.")
                    continue
        else:
            # KEYBOARD INPUT MODE
            user_input = input("You: ")
            
        # ... (Mode Control and Exit logic remains the same) ...
        if user_input.lower().strip() == 'enable voice assistant':
            if not voice_mode_enabled:
                voice_mode_enabled = True
                speak("Voice assistant enabled. I am now listening for your commands.")
            continue
            
        if user_input.lower().strip() == 'deactivate voice':
            if voice_mode_enabled:
                voice_mode_enabled = False
                speak("Voice assistant deactivated. Switching back to keyboard input.")
            continue

        if user_input.lower().strip() == 'exit':
            speak("Assistant shutting down. Goodbye!")
            break
            
        if not user_input.strip():
            continue

        # --- Gemini Interaction with Failover Logic ---
        
        MAX_RETRIES = len(VALID_API_KEYS) - current_api_key_index
        retries = 0
        response = None
        
        while retries < MAX_RETRIES:
            try:
                # 1. Send user message to the model
                response = chat.send_message(user_input)
                time.sleep(API_DELAY_SECONDS) 
                
                # 2. Tool Calling Loop (Inner loop)
                while response.function_calls:
                    function_responses = []
                    
                    for function_call in response.function_calls:
                        function_name = function_call.name
                        function_to_call = globals().get(function_name) 
                        
                        function_args = dict(function_call.args)
                        speak(f"Assistant action calling tool {function_name} with arguments.")
                        print(f"\n**ASSISTANT ACTION: Calling tool: {function_name}({function_args})**")

                        tool_output = function_to_call(**function_args)
                        print(f"**TOOL RESULT: {tool_output}**")

                        function_responses.append(
                            types.Content(
                                parts=[
                                    types.Part.from_function_response(
                                        name=function_name,
                                        response={"result": tool_output}
                                    )
                                ]
                            )
                        )

                    # Send the tool outputs back to the model 
                    response = chat.send_message(contents=function_responses)
                    time.sleep(API_DELAY_SECONDS) 
                
                # If everything succeeded, break the retry loop
                break 

            except errors.ServerError as e:
                # 503 UNAVAILABLE or other server issues
                retries += 1
                if retries < MAX_RETRIES:
                    speak(f"API Error: Server overloaded with current key (Key {current_api_key_index + 1}). Switching to next key.")
                    current_api_key_index += 1
                    # Re-initialize client/chat with the next key
                    if not initialize_client_and_chat(SYSTEM_INSTRUCTION_TEXT): # tools argument removed
                         speak("ERROR: Backup key failed during switch. Stopping attempts.")
                         return 
                    
                else:
                    speak("ERROR: All API keys have failed due to server overload. Please try again later.")
                    return 
            
            except Exception as e:
                # Catch all other API errors (e.g., 400 Invalid key, etc.)
                speak(f"An unexpected API error occurred: {e}. Switching to next key.")
                retries += 1
                if retries < MAX_RETRIES:
                    current_api_key_index += 1
                    if not initialize_client_and_chat(SYSTEM_INSTRUCTION_TEXT): # tools argument removed
                         speak("ERROR: Backup key failed during switch. Stopping attempts.")
                         return
                else:
                    speak("ERROR: All API keys have failed. Please check your keys and try again.")
                    return
        
        # Check if response was successfully populated
        if response and response.text:
            speak(response.text)
        elif response is None and retries >= MAX_RETRIES:
            pass
        else:
            speak("An unknown error occurred after processing the request.")


if __name__ == "__main__":
    run_assistant()