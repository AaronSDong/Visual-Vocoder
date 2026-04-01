import Wave

class WaveGroup:
    def __init__(self, f_list, wave_shape='sine'):
        self.active_waves = [3 for _ in range(len(f_list))]

        self.wave_list = []
        for freq in f_list:
            self.wave_list.append(Wave.Wave(wave_shape, t=0, f=freq))

    def play_wave(self, wave_num, t):
        self.wave_list[wave_num].play(t=t)
        self.active_waves[wave_num] = 3

    def deactive_wave_attempt(self, wave_num):
        self.active_waves[wave_num] -= 1
        if self.active_waves[wave_num] == 0:
            print('deactivated')
            self.wave_list[wave_num].pause()

    def stop_all(self):
        for wave in self.wave_list:
            wave.stop()