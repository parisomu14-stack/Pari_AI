import datetime
import os
import re
import sys
import webbrowser
from urllib.parse import quote_plus

import pyttsx3
import speech_recognition as sr
from google import genai
from google.genai import errors, types


def clean_key(k):
    return k.strip().strip('"').strip("'").strip()


# ---------- API key ----------
API_KEY = clean_key(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "")
if not API_KEY:
    print("GEMINI_API_KEY not found.")
    API_KEY = clean_key(input("Paste your Gemini API key here and press Enter: "))
    if not API_KEY:
        print("No key entered. Exiting.")
        sys.exit(1)
print(f"Using key: {API_KEY[:4]}... (length {len(API_KEY)})")

# ---------- Setup ----------
engine = pyttsx3.init()
recognizer = sr.Recognizer()
client = genai.Client(api_key=API_KEY)

MODELS = ["gemini-3.5-flash", "gemini-2.5-flash", "gemini-2.5-flash-lite"]
model_index = 0
chat = None
AI_OK = False
AI_PROBLEM = "AI is not available."

SYSTEM = ("You are Pari, a helpful voice assistant. Keep answers short, "
          "1 to 3 sentences, because they will be spoken aloud. "
          "Do not use markdown, bullet points or emojis.")


def check_ai():
    """Test the key and find a working model at startup."""
    global AI_OK, AI_PROBLEM, model_index
    print("Checking AI connection...")
    for i, name in enumerate(MODELS):
        try:
            client.models.generate_content(model=name, contents="Reply with the word OK")
            model_index = i
            AI_OK = True
            print("AI ready. Model:", name)
            return
        except errors.ClientError as e:
            code = getattr(e, "code", None)
            print(f"[{name}] error {code}: {e}")
            if code == 404:
                continue  # this model is not available, try the next one
            if code == 429:
                model_index = i
                AI_OK = True  # key is fine, only the quota is full
                print("Key works, but the free limit is reached for now.")
                return
            AI_PROBLEM = "The Gemini key was rejected. Check the error shown in the terminal."
            return
        except Exception as e:
            print(f"[{name}] error: {e}")
            AI_PROBLEM = "I could not connect to Gemini. Check your internet."
            return
    AI_PROBLEM = "No Gemini model is available for this key."


def new_chat():
    return client.chats.create(
        model=MODELS[model_index],
        config=types.GenerateContentConfig(system_instruction=SYSTEM),
    )


def speak(text):
    print("Pari:", text)
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("(Voice problem:", e, ")")


def listen():
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            except sr.WaitTimeoutError:
                return ""
    except (OSError, AttributeError):
        print("Microphone not found. Check your mic or install PyAudio.")
        sys.exit(1)

    try:
        text = recognizer.recognize_google(audio)
        print("You:", text)
        return text.lower()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        speak("Internet problem. Please check your connection.")
        return ""


def ask_ai(question):
    global chat
    if not AI_OK:
        return AI_PROBLEM
    try:
        if chat is None:
            chat = new_chat()
        response = chat.send_message(question)
        answer = (response.text or "").strip()
        return answer or "Sorry, I did not get an answer."
    except errors.ClientError as e:
        print("AI error:", e)
        code = getattr(e, "code", None)
        if code == 429:
            return "Too many requests. Please wait a minute and try again."
        return "Sorry, Gemini returned an error. Details are in the terminal."
    except Exception as e:
        print("AI error:", e)
        chat = None
        return "Sorry, I could not reach my AI brain right now."


def words(command):
    return set(re.findall(r"[a-z']+", command))


def handle_command(command):
    """Returns False to quit."""
    w = words(command)

    if w & {"exit", "stop", "bye", "goodbye"} and len(w) <= 3:
        speak("Goodbye!")
        return False
    elif "time" in w and len(w) <= 6:
        speak("The time is " + datetime.datetime.now().strftime("%I:%M %p"))
    elif "camera" in w and len(w) <= 5:
        speak("Opening camera")
        os.system("start microsoft.windows.camera:")
    elif "notepad" in w and len(w) <= 5:
        speak("Opening Notepad")
        os.system("start notepad")
    elif "calculator" in w and len(w) <= 5:
        speak("Opening Calculator")
        os.system("start calc")
    elif "open youtube" in command:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")
    elif "open google" in command:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")
    elif command.startswith("search"):
        query = command[len("search"):].strip()
        speak("Searching for " + query)
        webbrowser.open("https://www.google.com/search?q=" + quote_plus(query))
    else:
        speak(ask_ai(command))
    return True


# ---------- Main loop ----------
if __name__ == "__main__":
    check_ai()
    speak("Hello, I am Pari. How can I help you?")
    running = True
    try:
        while running:
            command = listen()
            if command:
                running = handle_command(command)
    except KeyboardInterrupt:
        print("\nStopped.")