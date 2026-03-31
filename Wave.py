import time
import pyaudio
import CreateWaveShape
import threading
import numpy as np

class Wave:
    def __init__(self, wave_shape='sine', t=0, f=440.0):
        # DEBUGGING VARIABLES
        self.sample_count = 0
        self.last_sample = 0

        self.f = f
        self.target_f = f
        self.sample_rate = 44100
        self.volume = .5
        note_multiple = 1.05946
        self.frequency_step = (note_multiple ** (1/30))

        self.output_bytes = None
        self.next_sample = 0
        self.wave_shape = CreateWaveShape.CreateWaveShape(wave_shape, self.sample_rate).array

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paFloat32, channels=1, rate=self.sample_rate, output=True)
        self.play(t=t)

    def get_next_chunk(self):
        samples_per_frequency = (len(self.wave_shape) - self.next_sample) // self.f

        if int((len(self.wave_shape) - self.next_sample) % self.f) != 0:
            sampling_range = range(int(samples_per_frequency)+1)
            wave_ends_at_zero = False
        else:
            sampling_range = range(int(samples_per_frequency))
            wave_ends_at_zero = True

        samples = np.array([self.wave_shape[round(self.next_sample + self.f*i)] for i in sampling_range])

        if wave_ends_at_zero:
            self.next_sample = 0
        else:
            location_of_last_sample = ((samples_per_frequency * self.f) + self.next_sample)
            self.next_sample = int(location_of_last_sample - len(self.wave_shape) + self.f)
            if self.next_sample >= self.f: self.next_sample = int(self.next_sample - self.f)

        # DEBUGGING
        # print(-samples[0]+self.last_sample, samples[1]-samples[0], self.wave_shape[1]-self.wave_shape[0], '\n', samples[-2]-samples[-1], end=' ')
        # print(samples[0], samples[1], '\n', samples[-2], samples[-1], self.next_sample, self.f, end=' ')
        # print(self.last_sample-samples[0], samples[1]-samples[0], abs(self.last_sample-samples[0]) - abs(samples[0]-samples[1]))
        # if abs(abs(self.last_sample-samples[0]) - abs(samples[0]-samples[1])) > .01 and (self.f != 200.3 and self.f != 440):
        #     print(self.f)
        #     print(self.last_sample, samples[0], samples[1])
        #     exit()

        self.last_sample = samples[-1]

        self.output_bytes = (self.volume * samples).tobytes()

    def play_loop(self, t=0):
        start_time = time.time()
        infinite_flag = True if t is None else False
        while (infinite_flag or time.time() - start_time < t) and self.playing:
            self.play_chunk()
            self.slide_frequency()

    def play(self, t=0):
        # remove previous thread
        self.playing = False
        time.sleep(.04)

        self.playing = True
        self.thread = threading.Thread(target=self.play_loop, kwargs={'t': t})
        self.thread.start()

    def play_chunk(self):
        start_time = time.time()

        self.get_next_chunk()
        self.stream.write(self.output_bytes)
        #print("Played sound for {:.8f} seconds".format(time.time() - start_time), self.sample_count)

    def set_target_frequency(self, frequency):
        self.target_f = frequency

    def set_direct_frequency(self, frequency):
        self.f = frequency

    def slide_frequency(self):
        if self.f == self.target_f: return

        f_is_lower_flag = self.f < self.target_f
        if self.f > self.target_f:
            self.f /= self.frequency_step
        else:
            self.f *= self.frequency_step

        # if pitch change overcompensates, set f to the target
        if f_is_lower_flag != (self.f < self.target_f): self.f = self.target_f

    def set_wave_shape(self, shape):
        self.wave_shape = CreateWaveShape.CreateWaveShape(shape, self.sample_rate).array

    def stop(self):
        self.playing = False
        self.thread.join()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


def main():
    sinewave = Wave(t=0, f=300)
    sinewave2 = Wave(t=0, f=300.6)
    sinewave.set_target_frequency(440)
    sinewave2.set_target_frequency(440)
    time.sleep(2)
    sinewave.play(4)
    sinewave2.play(4)
    time.sleep(2)
    sinewave.stop()
    sinewave2.stop()

if __name__ == '__main__':
    main()