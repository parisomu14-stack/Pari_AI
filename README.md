# Jarvis Voice Assistant

A simple voice assistant built with Python. It listens through your microphone, answers questions using the Google Gemini API, and speaks the reply aloud.

## Features
- Voice input using SpeechRecognition
- AI answers using Google Gemini (free tier available)
- Spoken replies using pyttsx3
- Local commands: tell the time, open YouTube, open Google, search the web, open Camera, Notepad and Calculator (Windows)
- Say "bye" or "stop" to exit

## Requirements
- Python 3.9 or later
- A microphone
- A free Gemini API key from https://aistudio.google.com/apikey

## Installation
```bash
pip install -r requirements.txt
```

## Usage
1. Set your API key (optional, otherwise the program asks for it):
   ```powershell
   setx GEMINI_API_KEY "your-key-here"
   ```
2. Run:
   ```bash
   python JARVIS_gemini.py
   ```

## Example commands
- "What time is it"
- "Open YouTube"
- "Search python tutorials"
- "Open the camera"
- Any question, for example "What is the capital of France"

## Note
Never upload your API key to GitHub. This project reads the key from an environment variable or asks for it when it starts.
