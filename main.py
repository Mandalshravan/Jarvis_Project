# Import necessary libraries
import speech_recognition as sr                 # For converting speech to text
import webbrowser                               # For opening websites
import pyttsx3                                  # For text-to-speech conversion
import musicLibrary                             # Custom module containing song titles and links
import requests                                 # For making HTTP requests (used to fetch news)
import os                                       # For accessing environment variables (not used directly here)
from azure.ai.inference import ChatCompletionsClient                  # Azure client for chat completion
from azure.ai.inference.models import SystemMessage, UserMessage      # Message formats for the chat model
from azure.core.credentials import AzureKeyCredential                 # Credential handling for Azure

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# News API key (used to fetch top news headlines)
newsapi = "fd240dad0099476cae7b23086355cafd"

# GPT-4.1 API setup using Azure client (Replace token with secure method in production)
endpoint = "https://models.github.ai/inference"          # API endpoint
model = "openai/gpt-4.1"                                 # Model name
token = "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"                        # API token (use environment variable in real-world use)---token = "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"

# Create an Azure client using the provided token
client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

# Function to make the assistant speak out text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to send user query to GPT model and get response
def askJarvis(message):
    response = client.complete(
        messages=[
            SystemMessage("You are a helpful voice assistant named Jarvis."),  # System role definition
            UserMessage(message)                                              # User query
        ],
        temperature=1,      # Controls randomness of response
        top_p=1,            # Controls diversity of response
        model=model         # Model to use
    )
    return response.choices[0].message.content  # Return AI-generated response

# Function to process user voice commands
def processCommand(c):
    c = c.lower()  # Convert command to lowercase for easy comparison
    
    # Open various websites based on command
    if "open google" in c:
        speak("Opening Google")
        webbrowser.open("https://google.com")
    elif "open facebook" in c:
        speak("Opening Facebook")
        webbrowser.open("https://facebook.com")
    elif "open youtube" in c:
        speak("Opening YouTube")
        webbrowser.open("https://youtube.com")
    elif "open linkedin" in c:
        speak("Opening LinkedIn")
        webbrowser.open("https://linkedin.com")

    # Play song from music library if command starts with "play"
    elif c.startswith("play"):
        song = c[5:].strip().lower()  # Extract song name after "play"
        found = False
        for title in musicLibrary.music:
            if title.lower() == song:
                speak(f"Playing {title}")
                webbrowser.open(musicLibrary.music[title])
                found = True
                break
        if not found:
            speak("Sorry, I couldn't find that song.")

    # Fetch and speak top news headline
    elif "news" in c.lower():
        r = requests.get("https://newsapi.org/v2/top-headlines?country=us&apiKey=" + newsapi)
        if r.status_code == 200:
            data = r.json()
            if 'articles' in data and len(data['articles']) > 0:
                headline = data['articles'][0]['title']
                print("Top Headline:", headline)
                speak("Top headline is: " + headline)
            else:
                speak("No headlines found.")
        else:
            speak("Failed to fetch the news.")

    # If command doesn't match any predefined category, ask GPT (Jarvis)
    else:
        speak("Let me think...")
        try:
            reply = askJarvis(c)     # Send to GPT model
            print("Jarvis:", reply)
            speak(reply)             # Speak out GPT's response
        except Exception as e:
            print("AI Error:", e)
            speak("I'm sorry, I couldn't process that.")

# Main block: starts listening and processing user commands
if __name__ == "__main__":
    speak("Initializing Jarvis....")  # Initial greeting
    while True:
        r = sr.Recognizer()           # Initialize speech recognizer
        r.energy_threshold = 300      # Minimum audio energy to consider
        r.pause_threshold = 0.8       # Pause duration to complete a phrase

        try:
            # Listen for wake word using microphone
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=1)
                print("Listening for wake word...")
                audio = r.listen(source, timeout=3, phrase_time_limit=2)
                word = r.recognize_google(audio)   # Convert speech to text
                print("Heard:", word)

            # If wake word "Jarvis" detected, proceed to listen to command
            if word.lower() == "jarvis":
                speak("Yes?")
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=0.5)
                    print("Jarvis Active, listening for command...")
                    audio = r.listen(source)
                    command = r.recognize_google(audio)  # Convert command speech to text
                    print("Command:", command)
                    processCommand(command)             # Process the recognized command

        # Catch and print any exceptions (like timeout or recognition errors)
        except Exception as e:
            print("Error:", e)
