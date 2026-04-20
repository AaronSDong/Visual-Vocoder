import time
import numpy as np
import pyaudio


class SineWave:
    def __init__(self):
        self.f = 440
        self.target_f = 440
        self.sample_rate = 44100
        self.volume = .5
        note_multiple = 1.05946
        self.frequency_step = (note_multiple ** (1/8))
        self.steps_per_second = 100
        self.duration = 1 / self.steps_per_second

        self.output_bytes = None
        self.last_sample = 0
        self.falling_end_phase_flag = False

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paFloat32, channels=1, rate=self.sample_rate, output=True)

    def get_next_chunk(self):
        # eliminate phase shift issues
        phase_start = np.arcsin(self.last_sample)
        if self.falling_end_phase_flag: phase_start = (np.pi / 2) + abs(phase_start - (np.pi / 2))
        range_start = (phase_start * self.sample_rate / (2 * np.pi * self.f)) + 1

        # generate samples, note conversion to float32 array
        phase_shifted_ranges = np.arange(range_start, (self.sample_rate * self.duration) + range_start)
        samples = (np.sin(2 * np.pi * phase_shifted_ranges * self.f / self.sample_rate)).astype(np.float32)

        # update flag if wave ends in a falling phase
        self.falling_end_phase_flag = samples[-2] > samples[-1]

        self.output_bytes = (self.volume * samples).tobytes()
        self.last_sample = samples[-1]

    def play(self, t):
        start_time = time.time()
        while time.time() - start_time < t:
            self.play_chunk()
            self.slide_frequency()

    def play_chunk(self):
        start_time = time.time()

        self.get_next_chunk()
        self.stream.write(self.output_bytes)
        #print("Played sound for {:.2f} seconds".format(time.time() - start_time))

    def set_target_frequency(self, frequency):
        self.target_f = frequency

    def set_direct_frequency(self, frequency):
        self.f = frequency

    def slide_frequency(self):
        if self.f == self.target_f: return

        f_is_lower_flag = self.f < self.target_f
        self.f *= self.frequency_step

        # if pitch change overcompensates, set f to the target
        if f_is_lower_flag != (self.f < self.target_f): self.f = self.target_f

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


def main():
    sinewave = SineWave()
    sinewave.set_target_frequency(880)
    sinewave.play(5)
    sinewave.stop()


main()