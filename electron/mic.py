import speech_recognition as sr
import sounddevice as sd
import numpy as np

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

def main():
    # test_microphone()
    transcribe()

if __name__ == "__main__":
    main()