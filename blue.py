import os
import google.generativeai as genai
import requests
from gtts import gTTS
import pygame
import speech_recognition as sr
import webbrowser

# Set your API keys here for testing purposes
os.environ["GEMINI_API_KEY"] = 'AIzaSyAJt60U4IyFrZJwKh7uad7nNh7hTgzestg'
os.environ["newsapi_key"] = 'aa62815f1896466eab953ddd11a0891f'

# Configure Google Generative AI
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)

def generate_ai_response(prompt):
    chat_session = model.start_chat(
        history=[
            {"role": "user", "parts": [prompt]}
        ]
    )
    response = chat_session.send_message(prompt)
    return response.text

def speak(text):
    tts = gTTS(text)
    tts.save('temp.mp3')

    pygame.mixer.init()
    pygame.mixer.music.load('temp.mp3')
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.stop()
    pygame.mixer.quit()

    os.remove('temp.mp3')

def processCommand(c):
    print(f"Command: {c}")

    if "how are you" in c.lower():
        speak("I am just a program, so I don't have feelings, but I'm here to help you.")
    elif "open google" in c.lower():
        webbrowser.open("https://google.com")
    elif "open facebook" in c.lower():
        webbrowser.open("https://facebook.com")
    elif "open youtube" in c.lower():
        webbrowser.open("https://youtube.com")
    elif "open linkedin" in c.lower():
        webbrowser.open("https://linkedin.com")
    elif "news" in c.lower():
        r = requests.get(f"https://newsapi.org/v2/top-headlines?country=in&apiKey={os.environ.get('newsapi_key')}")
        if r.status_code == 200:
            data = r.json()
            articles = data.get('articles', [])
            for article in articles:
                speak(article['title'])
                pygame.mixer.music.stop()
    elif any(op in c for op in ["+", "-", "*", "/"]):
        try:
            result = eval(c)
            speak(f"The result is {result}")
        except Exception:
            speak("Sorry, I couldn't understand the arithmetic expression.")
    elif "reset" in c.lower():
        return "reset"
    else:
        ai_response = generate_ai_response(c)
        print(f"Response: {ai_response}")
        speak(ai_response)
    return None

def listen_for_command():
    recognizer = sr.Recognizer()
    print("Listening for commands...")
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=2)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
            print("Audio captured.")
            try:
                command = recognizer.recognize_google(audio)
                print(f"Command recognized: {command}")
                return command
            except sr.UnknownValueError:
                print("Could not understand command")
                speak("Sorry, I did not understand that.")
            except sr.RequestError as e:
                print(f"Could not request results for command; {e}")
                speak("Sorry, there was an error processing your command.")
    except sr.WaitTimeoutError:
        print("Timeout waiting for command.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    while True:
        user_choice = input("Do you want to use voice commands or type instructions? (v/t): ").strip().lower()

        if user_choice == "v":
            command = listen_for_command()
            if command:
                processCommand(command)
        elif user_choice == "t":
            while True:
                command = input("Enter your command: ").strip().lower()
                result = processCommand(command)
                if result == "reset":
                    break
        else:
            print("Invalid choice. Please enter 'v' for voice or 't' for typing.")
