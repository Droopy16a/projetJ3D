from gtts import gTTS
import soundfile as sf
import io

# Generate MP3 into memory
text = "Hello, how are you?"
tts = gTTS(text=text, lang='en')

mp3_fp = io.BytesIO()
tts.write_to_fp(mp3_fp)
mp3_fp.seek(0)

# Decode MP3 to WAV using soundfile
data, samplerate = sf.read(mp3_fp)
sf.write("hello.wav", data, samplerate)
print("hello.wav created")
