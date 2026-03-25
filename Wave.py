import time
import pyaudio
import CreateWaveShape
import threading

class Wave:
    def __init__(self, wave_shape='sine'):
        # DEBUGGING VARIABLES
        self.sample_count = 0
        self.last_sample = 0

        self.f = 440
        self.target_f = 440
        self.sample_rate = 44100
        self.volume = .5
        note_multiple = 1.05946
        self.frequency_step = (note_multiple ** (1/30))

        self.output_bytes = None
        self.next_sample = 0
        self.wave_shape = CreateWaveShape.CreateWaveShape(wave_shape, self.sample_rate).array

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paFloat32, channels=1, rate=self.sample_rate, output=True)

    def get_next_chunk(self):
        samples = self.wave_shape[self.next_sample::int(self.f)]
        self.next_sample = int(self.f - ((len(self.wave_shape) - self.next_sample) % self.f))
        if self.next_sample == self.f: self.next_sample = 0

        # DEBUGGING
        #self.sample_count += len(samples)
        #print(self.next_sample, (len(self.wave_shape) // self.f)*self.f)
        #print(samples[0], samples[1], '\n', samples[-2], samples[-1], self.next_sample, end=' ')

        self.output_bytes = (self.volume * samples).tobytes()
        self.last_sample = samples[-1]

    def play_loop(self, t=0):
        start_time = time.time()
        infinite_flag = True if t==0 else False
        while (time.time() - start_time < t or infinite_flag) and self.playing:
            self.play_chunk()
            self.slide_frequency()

    def play(self, t=0):
        # remove previous thread
        self.playing = False
        time.sleep(.04)

        self.playing = True
        self.thread = threading.Thread(target=self.play_loop, kwargs={'t': t}, daemon=True)
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
    sinewave = Wave()
    sinewave.play(t=3)
    sinewave.set_target_frequency(300.10354182)
    time.sleep(1)
    sinewave.play(t=3)
    sinewave.set_target_frequency(500.10354182)
    time.sleep(3)
    sinewave.stop()

if __name__ == '__main__':
    main()