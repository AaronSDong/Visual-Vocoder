import pyaudio
import numpy as np

CHUNK = 1024
RATE = 44100
FORMAT = pyaudio.paFloat32

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)
output_stream = p.open(format=pyaudio.paFloat32, channels=1, rate=RATE, output=True)

print("Recording...")
for _ in range(10000):  # Read 100 chunks
    raw = stream.read(CHUNK)
    audio_np = np.frombuffer(raw, dtype=np.double)  # Shape: (1024,)
    print(max(audio_np))
    output_bytes = audio_np.tobytes()
    output_stream.write(output_bytes)

stream.stop_stream()
stream.close()
p.terminate()