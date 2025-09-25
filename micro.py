import speech_recognition as sr
import time

r = sr.Recognizer()
print(sr.Microphone.list_microphone_names())

def callback(recognizer, audio, texts):
    try:
        text = recognizer.recognize_google(audio)
        print("You said:", text)
        texts.append(text)
    except sr.UnknownValueError:
        print("Could not understand")
    except sr.RequestError as e:
        print("API error:", e)


if __name__ == "__main__":
    mic = sr.Microphone()

    with mic as source:
        r.adjust_for_ambient_noise(source)

    stop_listening = r.listen_in_background(mic, callback)

    print("Listening in background... (press Ctrl+C to stop)")

    while True:
        time.sleep(0.1)
