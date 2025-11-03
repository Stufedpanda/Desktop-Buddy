import numpy as np
import sounddevice as sd
from piper import PiperVoice, SynthesisConfig

voice = PiperVoice.load("en_GB-cori-high.onnx", use_cuda=True)

# syn_config = SynthesisConfig(
#     volume=0.3,  # half as loud
#     length_scale=0.9,  # twice as slow
#     noise_scale=0.9,  # more audio variation
#     noise_w_scale=1.0,  # more speaking variation
#     normalize_audio=False, # use raw audio from voice
# )

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
    print("Type a line; streaming starts immediately. Enter to quit.")
    while True:
        line = input("> ").strip()
        if not line:
            break
        stream_speech(line)

if __name__ == "__main__":
    main()