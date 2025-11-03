import speech_recognition as sr
import sounddevice as sd
import numpy as np

from ollama import chat
from ollama import ChatResponse

from piper import PiperVoice, SynthesisConfig

voice = PiperVoice.load("en_GB-cori-high.onnx", use_cuda=True)

def load_system_prompt(path="system_prompt.txt"):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def test_microphone():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Say something...")
        audio = recognizer.listen(source, timeout=5)
    
    sr_play = audio.sample_rate
    samples = np.frombuffer(audio.get_raw_data(), dtype=np.int16).astype(np.float32) / 32768.0

    print("Playing back...")
    sd.play(samples, samplerate=sr_play)
    sd.wait()

def transcribe():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Say something...")
        audio = recognizer.listen(source, timeout=5)
    
    try:
        text = recognizer.recognize_google(audio)
        print("You said: " + text)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
    
    return text

def llm_response(user_input: str) -> str:

    system_prompt = {
            'role': 'system',
            'content': load_system_prompt("personality.txt")
    }

    # User’s message
    user_message = {
        'role': 'user',
        'content': user_input
    }

    # Send to Ollama
    response: ChatResponse = chat(
        model='gemma3',
        messages=[system_prompt, user_message],
        options={
            'temperature': 0.4,   # more concise
            'top_p': 0.8,
            'num_predict': 500     # limit reply length
        }
    )

    return response.message.content

def stream_speech(text: str):
    # Prime one chunk to get the audio format
    gen = voice.synthesize(
        text
    )
    first = next(gen, None)
    if first is None:
        return

    sr = first.sample_rate          # typically 22050
    ch = first.sample_channels      # 1
    dtype = "int16"                 # matches audio_int16_bytes

    with sd.OutputStream(samplerate=sr, channels=ch, dtype=dtype, latency="low") as stream:
        stream.write(np.frombuffer(first.audio_int16_bytes, dtype=np.int16))
        for chunk in gen:
            stream.write(np.frombuffer(chunk.audio_int16_bytes, dtype=np.int16))

def main():
    text = transcribe()
    response = llm_response(text)
    print("LLM Response:", response)
    stream_speech(response)



if __name__ == "__main__":
    main()