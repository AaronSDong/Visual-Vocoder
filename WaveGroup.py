import Wave

class WaveGroup:
    def __init__(self, f_list=None, wave_shape='sine', mono=True):
        if f_list is None:
            # Just intonation at C4=256Hz, Major Scale
            f_list = [256, 288, 320, 341.33, 384, 426.67, 480, 512]

        self.active_waves = [3 for _ in range(len(f_list))]  # 3 represents counter till deactivation
        self.wave_list = []

        for freq in f_list:
            self.wave_list.append(Wave.Wave(wave_shape, t=0, f=freq, mono=mono))

    def play_wave(self, wave_num, t):
        self.wave_list[wave_num].play(t=t)
        self.active_waves[wave_num] = 3

    def deactive_wave_attempt(self, wave_num):
        self.active_waves[wave_num] -= 1
        if self.active_waves[wave_num] == 0:
            print('deactivated' + str(wave_num))
            self.wave_list[wave_num].pause()

    def set_vol_all(self, volume, channel='mono'):
        for wave in self.wave_list:
            wave.set_volume(volume, channel=channel)

    def stop_all(self):
        for wave in self.wave_list:
            wave.stop()