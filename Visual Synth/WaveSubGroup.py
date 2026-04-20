# Old code, currently unused

import Wave
import random
import time
from math import floor, ceil

class WaveSubGroup:
    def __init__(self, wave_shape='sine', mono=True, freq=440, max_vol=1, delay=0.005):
        self.sub_wave_count = 3
        self.depth = .005  # Will range from .5ms to 100 ms
        self.delay = delay  # Will range from .5ms to 100 ms
        self.rate = .05  # Will range from .05 Hz to 10 Hz
        self.dry_wet = 100  # Will range from 0-100%

        self.wave_list = []
        self.wave_list.append(Wave.Wave(wave_shape=wave_shape, mono=mono, f=freq, max_vol=max_vol))
        freq_list = []

        # determine which frequencies are needed
        for i in range(floor(self.sub_wave_count-1)):
            changed_freq = 'e'  # Edit low frequencies
            freq_list.append(changed_freq)
        for i in range(ceil(self.sub_wave_count-1)):
            changed_freq = 'e'  # Edit high frequencies
            freq_list.append(changed_freq)

        for i in range(len(self.wave_list)):
            delay = random.uniform(0.5, 1.5) * self.delay
            time.sleep(delay)
            self.wave_list.append(Wave.Wave(wave_shape=wave_shape, mono=mono, f=freq, max_vol=max_vol))