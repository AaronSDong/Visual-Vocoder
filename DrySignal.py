import time
import CreateWaveShape
import numpy as np

class DrySignal:
    def __init__(self, wave_shape='sine', f=440.0, max_vol=1.0, mono=True, frequency_step=None):
        # DEBUGGING VARIABLES
        self.sample_count = 0
        self.last_sample = 0

        self.sample_rate = 44100
        self.f = f
        self.target_f = f
        self.frequency_step_linear = False
        self.frequency_step = frequency_step
        if frequency_step is None:
            note_multiple = 1.05946
            self.frequency_step = (note_multiple ** (1/30))

        self.volume_left = 0
        self.target_volume_left = max_vol
        self.max_volume_left = max_vol
        self.volume_right = 0
        self.target_volume_right = max_vol
        self.max_volume_right = max_vol
        self.volume_step = .01

        self.output_bytes = None
        self.next_sample = 0
        self.wave_shape = CreateWaveShape.CreateWaveShape(wave_shape, self.sample_rate).array

        # channel_count = 1 if mono else 2
        self.mono = mono
        self.playing = True
        # self.p = pyaudio.PyAudio()
        # self.stream = self.p.open(format=pyaudio.paFloat32, channels=channel_count, rate=self.sample_rate, output=True)
        # self.thread = None
        # self.play(t=t)

    def __init__get_next_chunk(self):
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
        # #     exit()
        # self.last_sample = samples[-1]

        if self.mono:
            return (self.volume_left * samples).astype(np.float32)
            # self.output_bytes = (self.volume_left * samples).astype(np.float32).tobytes()
        else:
            left_channel = (self.volume_left * samples)
            right_channel = (self.volume_right * samples)
            interweaved_channels = np.ravel(np.column_stack((left_channel, right_channel))).astype(np.float32)
            return interweaved_channels
            # self.output_bytes = interweaved_channels.tobytes()

    def get_next_sample(self):
        next_sample_value = self.wave_shape[int(self.next_sample)]
        self.next_sample += self.f
        if self.next_sample >= self.sample_rate:
            self.next_sample = self.f + self.next_sample - self.sample_rate
        return np.array([next_sample_value])

    # def play_loop(self, t=0.0):
    #     start_time = time.time()
    #     infinite_flag = True if t is None else False
    #     while (infinite_flag or time.time() - start_time < t) and self.playing:
    #         self.play_chunk()
    #         self.slide_frequency()
    #         self.slide_volume('left')
    #         self.slide_volume('right')
    #
    #     while self.volume_left != self.target_volume_left and self.volume_right != self.target_volume_right:
    #         self.play_chunk()
    #         self.slide_volume(channel='left')
    #         self.slide_volume(channel='right')
    #
    # def play(self, t=None):
    #     self.target_volume_left = 0
    #     self.target_volume_right = 0
    #     self.playing = False
    #     time.sleep(.04)
    #
    #     self.playing = True
    #     self.volume_left = 0
    #     self.volume_right = 0
    #     self.target_volume_left = self.max_volume_left
    #     self.target_volume_right = self.max_volume_right
    #     self.next_sample = 0
    #     self.thread = threading.Thread(target=self.play_loop, kwargs={'t': t})
    #     self.thread.start()

    def receive_chunk(self):
        samples = self.__init__get_next_chunk()
        self.__init__slide_frequency()
        self.__init__slide_volume('left')
        self.__init__slide_volume('right')
        return samples
        # self.stream.write(self.output_bytes)

    # def pause(self):
    #     self.target_volume_left = 0
    #     self.target_volume_right = 0
    #
    #     # remove previous thread
    #     self.playing = False
    #     time.sleep(.04)

    def set_frequency(self, frequency, linear=False, frequency_step=None):
        self.target_f = frequency
        self.frequency_step_linear = linear
        if frequency_step is not None: self.frequency_step = frequency_step

    def set_direct_frequency(self, frequency):
        self.f = frequency
        self.target_f = frequency

    def __init__slide_frequency(self):
        if self.f == self.target_f: return
        f_is_lower_flag = self.f < self.target_f

        # Change frequency based on very funny and not poorly coded tree
        if self.f > self.target_f:
            if self.frequency_step_linear:
                self.f -= self.frequency_step
            else:
                self.f /= self.frequency_step
        else:
            if self.frequency_step_linear:
                self.f += self.frequency_step
            else:
                self.f *= self.frequency_step

        # if pitch change overcompensates, set f to the target
        if f_is_lower_flag != (self.f < self.target_f): self.f = self.target_f

    def set_volume(self, volume, channel):
        if self.mono or channel.lower() in ('left', 'mono'):
            self.max_volume_left = volume
            self.target_volume_left = volume

        if self.mono or channel.lower() in ('right', 'mono'):
            self.max_volume_right = volume
            self.target_volume_right = volume

    def set_direct_volume(self, volume, channel):
        if self.mono or channel.lower() in ('left', 'mono'):
            self.volume_left = volume
            self.target_volume_left = volume
            if self.max_volume_left < volume: self.max_volume_left = volume

        if self.mono or channel.lower() in ('right', 'mono'):
            self.volume_right = volume
            self.target_volume_right = volume
            if self.max_volume_right < volume: self.max_volume_right = volume

    def __init__slide_volume(self, channel):
        if channel == 'left':
            volume = getattr(self, 'volume_left')  # getattr idea taken from AI
            target_volume = getattr(self, 'target_volume_left')
        else:
            volume = getattr(self, 'volume_right')
            target_volume = getattr(self, 'target_volume_right')

        if volume == target_volume: return
        elif abs(volume - target_volume) < self.volume_step:
            volume = target_volume

        else:
            if volume > target_volume:
                volume -= self.volume_step
            else:
                volume += self.volume_step

        setattr(self, 'volume_left', volume) if channel == 'left' else setattr(self, 'volume_right', volume)

    def set_wave_shape(self, shape):
        self.wave_shape = CreateWaveShape.CreateWaveShape(shape, self.sample_rate).array

    # def stop(self):
    #     self.playing = False
    #     self.thread.join()
    #     self.stream.stop_stream()
    #     self.stream.close()
    #     self.p.terminate()


def main():
    freq_list = [434, 444]
    wave5 = DrySignal(f=434, wave_shape='sine', max_vol=1)  # vol is dry/wet
    wave1 = DrySignal(f=440, wave_shape='sine')
    wave3 = DrySignal(f=444, wave_shape='sine', max_vol=1)
    wave_list = [wave3, wave5]
    time.sleep(2)
    for w in wave_list:
        time.sleep(0.2)  # delay
    time.sleep(5)
    start_time = time.time()
    for _ in range(100):
        for i in range(len(wave_list)):
            print(time.time()-start_time)
            w = wave_list[i]
            f = freq_list[i]
            f += (f-440)//2  # depth
            w.set_frequency(f)
        time.sleep(.015)  # speed (also change how fast freq step)
        for i in range(len(wave_list)):
            w = wave_list[i]
            f = freq_list[i]
            f -= (f-440)//4
            w.set_frequency(f)
        time.sleep(.015)


if __name__ == '__main__':
    main()