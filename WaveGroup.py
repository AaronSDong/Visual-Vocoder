import Wave
import numpy as np

class WaveGroup:
    def __init__(self, f_list=None, wave_shape='sine', mono=True, octave=2, key='C', scale='major', max_vol=1):
        self.octave_set_buffer = [octave, 3]  # first value is attempted octave, second is frames to buffer

        self.octave_shift = octave
        self.octave_multiplier = (octave + 2) - 4  # Translate octave where the 2nd octave is equal to C4
        self.key_shifter = 2 ** (self.get_key_index(key) / 12)  # equal temperament factor
        self.scale = self.get_scale(scale.lower())

        if f_list is None:
            self.f_list = self.scale * self.key_shifter * (2**self.octave_multiplier)
        else:
            self.f_list = f_list

        self.active_waves = [3 for _ in range(len(self.f_list))]  # 3 represents counter till deactivation
        self.wave_list = []

        for freq in self.f_list:
            self.wave_list.append(Wave.Wave(wave_shape=wave_shape, t=0, f=freq, mono=mono, max_vol=max_vol))

    def play_wave(self, wave_num, t):
        self.wave_list[wave_num].play(t=t)
        self.active_waves[wave_num] = 3

    def deactive_wave_attempt(self, wave_num):
        self.active_waves[wave_num] -= 1
        if self.active_waves[wave_num] == 0:
            self.wave_list[wave_num].pause()

    def octave_set_attempt(self, new_octave):
        if new_octave != self.octave_set_buffer[0] or new_octave == self.octave_shift:
            self.octave_set_buffer = [new_octave, 3]

        else:
            self.octave_set_buffer[1] -= 1
            if self.octave_set_buffer[1] == 0: self._internal_adjust_octave(new_octave)

    def set_vol_all(self, volume, channel='mono'):
        for wave in self.wave_list:
            wave.set_volume(volume, channel=channel)

    def adjust_key_and_scale(self, key=None, scale=None):
        if key is not None: self.key_shifter = (self.get_key_index(key)) * (2**(1/12))  # equal temperament factor
        if scale is not None: self.scale = self.get_scale(scale.lower())

        self.f_list = self.scale * self.key_shifter * (2 ** self.octave_multiplier)
        self.shift_freq()

    def _internal_adjust_octave(self, octave):
        octave_shift = octave - self.octave_shift
        self.octave_shift = octave  # Translate octave where the 2nd octave is equal to C4
        self.octave_multiplier = (octave + 2) - 4
        self.f_list = self.f_list * (2**octave_shift)
        self.shift_freq()

    def shift_freq(self):
        for i, freq in enumerate(self.f_list):
            self.wave_list[i].set_direct_frequency(freq)

    def stop_all(self):
        for wave in self.wave_list:
            wave.stop()

    # dictionaries below here were created by AI
    @staticmethod
    def get_key_index(key):
        # Index relative to C (going up)
        index = {
            'C': 0, 'B#': 0, 'Dbb': 0,
            'C#': 1, 'Db': 1,
            'D': 2, 'C##': 2, 'Ebb': 2,
            'D#': 3, 'Eb': 3,
            'E': 4, 'Fb': 4, 'D##': 4,
            'F': 5, 'E#': 5, 'Gbb': 5,
            'F#': 6, 'Gb': 6,
            'G': 7, 'F##': 7, 'Abb': 7,
            'G#': 8, 'Ab': 8,
            'A': 9, 'G##': 9, 'Bbb': 9,
            'A#': 10, 'Bb': 10,
            'B': 11, 'Cb': 11, 'A##': 11
        }

        return index[key]
    @staticmethod
    def get_scale(scale):
        # All scales are in Just Intonation, starting at C4 (list of frequencies)
        scale_list = {
            "major": [256.0, 288.0, 320.0, 341.33, 384.0, 426.67, 480.0, 512.0],
            "minor": [256.0, 288.0, 307.2, 341.33, 384.0, 409.6, 460.8, 512.0],
            "harmonic_minor": [256.0, 288.0, 307.2, 341.33, 384.0, 409.6, 480.0, 512.0],
            "blues": [256.0, 307.2, 341.33, 360.0, 384.0, 426.67, 460.8, 512.0],
            "dorian": [256.0, 288.0, 307.2, 341.33, 384.0, 426.67, 460.8, 512.0],
            "phrygian": [256.0, 273.07, 307.2, 341.33, 384.0, 409.6, 460.8, 512.0],
            "lydian": [256.0, 288.0, 320.0, 360.0, 384.0, 426.67, 480.0, 512.0],
            "mixolydian": [256.0, 288.0, 320.0, 341.33, 384.0, 426.67, 460.8, 512.0],
            "locrian": [256.0, 273.07, 307.2, 341.33, 364.09, 409.6, 460.8, 512.0]
        }

        return np.array(scale_list[scale])