import Wave
from SettingsScript import getScale
from ChorusSettings import ChorusSettings

class WaveGroup:
    def __init__(self, f_list=None, wave_shape='sine', mono=True, octave=2, key='C', scale='major', max_vol=1,
                 chorus=ChorusSettings()):
        self.octave_set_buffer = [octave, 3]  # first value is attempted octave, second is frames to buffer
        self.chorus_hand = 'left'
        self.chorus_bypass = False

        self.octave_shift = octave
        self.octave_multiplier = (octave + 2) - 4  # Translate octave where the 2nd octave is equal to C4
        self.key = key
        self.scale_type = scale
        self.scale = getScale(scale, key)

        if f_list is None:
            self.f_list = self.scale * (2**self.octave_multiplier)
        else:
            self.f_list = f_list  # Custom chosen notes

        self.active_waves = [3 for _ in range(len(self.f_list))]  # 3 represents counter till deactivation
        self.wave_list = []

        for freq in self.f_list:
            self.wave_list.append(Wave.Wave(wave_shape=wave_shape, t=0, f=freq, mono=mono, max_vol=max_vol,
                                            chorus=chorus))

    def play_wave(self, wave_num, t, max_vol=1):
        self.wave_list[wave_num].play(t=t, max_vol=max_vol)
        self.active_waves[wave_num] = 3

    def deactivate_wave_attempt(self, wave_num):
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

    def adjust_key_and_scale(self, key=None, scale_type=None):
        if key is None: key = self.key
        if scale_type is None: scale_type = self.scale_type
        self.key = key
        self.scale = scale_type
        scale = getScale(key, scale_type)

        self.f_list = scale * (2 ** self.octave_multiplier)
        self.shift_freq()

    def _internal_adjust_octave(self, octave):
        octave_shift = octave - self.octave_shift
        self.octave_shift = octave  # Translate octave where the 2nd octave is equal to C4
        self.octave_multiplier = (octave + 2) - 4
        self.f_list = self.f_list * (2**octave_shift)
        self.shift_freq()

    def update_chorus(self, chorus):
        for wave in self.wave_list:
            wave.update_chorus_settings(chorus)

    def shift_freq(self):
        for i, freq in enumerate(self.f_list):
            self.wave_list[i].set_direct_frequency(freq)

    def stop_all(self):
        for wave in self.wave_list:
            wave.stop()

# Example demonstration written by AI

def main():
    import time

    # Setup the synth
    settings = ChorusSettings()
    synth = WaveGroup(
        wave_shape='sine',
        key='G',
        scale='major',
        octave=2,
        max_vol=0.5,
        chorus=settings
    )

    # A 4-chord progression indices: G (I), D (V), Em (vi), C (IV)
    progression = [
        [0, 2, 4],  # Chord 1
        [4, 6, 1],  # Chord 2
        [5, 0, 2],  # Chord 3
        [3, 5, 0]  # Chord 4
    ]

    bpm = 100
    beat_duration = 60 / bpm

    print("Playing... Press Ctrl+C to stop.")

    try:
        while True:  # Loop the song indefinitely
            for chord in progression:
                # 1. PLAY THE CHORD
                for note_index in chord:
                    synth.play_wave(note_index, t=100, max_vol=.5)

                # 2. HOLD THE NOTES
                time.sleep(beat_duration)

                # 3. DEACTIVATE (The "3-attempt" logic)
                # Your code requires 3 calls to reach 0 and trigger wave.pause()
                for note_index in chord:
                    synth.deactivate_wave_attempt(note_index)
                    synth.deactivate_wave_attempt(note_index)
                    synth.deactivate_wave_attempt(note_index)

                # Small gap between chords to prevent muddy transitions
                time.sleep(0.05)

    except KeyboardInterrupt:
        synth.stop_all()
        print("\nSong stopped.")

if __name__ == "__main__":
    main()