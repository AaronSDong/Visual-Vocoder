# Code partially taken from a sample file, some edits added with AI help

from __future__ import division, print_function
import numpy as np
import pyworld as pw
import pyaudio

def main():
    sample_rate = 44100
    chunk = 8192
    p = pyaudio.PyAudio()
    input_stream = p.open(format=pyaudio.paFloat32, channels=1, rate=sample_rate, input=True, frames_per_buffer=chunk)
    output_stream = p.open(format=pyaudio.paFloat32, channels=1, rate=sample_rate, output=True)

    while True:
        raw = input_stream.read(chunk)
        audio_np = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
        audio_np = audio_np * 2  # input gain

        root_mean_squared = np.sqrt(np.mean(audio_np ** 2))
        if root_mean_squared < .005:
            output_stream.write(np.zeros(chunk, dtype=np.float32).tobytes())
            continue

        frequency, spectral_envelope, ap = pw.wav2world(audio_np, sample_rate)

        t = np.arange(len(frequency))
        frequency = 200 + (15 * np.sin(2 * np.pi * t / 50))
        ap[:] = 0

        y = pw.synthesize(frequency, spectral_envelope, ap, sample_rate, pw.default_frame_period)
        y = y.astype(np.float32)
        output_bytes = y.tobytes()
        output_stream.write(output_bytes)


if __name__ == '__main__':
    main()