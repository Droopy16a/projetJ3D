from vosk import Model, KaldiRecognizer
import pyaudio
import json

model = Model("model-small")  # Download from Vosk website
rec = KaldiRecognizer(model, 16000)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1,
                rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()

while True:
    data = stream.read(4000, exception_on_overflow = False)
    if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())
        if "text" in result and result["text"]:
            print("Command:", result["text"])
