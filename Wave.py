import time
import pyaudio
import threading
import numpy as np
from DrySignal import DrySignal
from ChorusSettings import ChorusSettings

class Wave:
    def __init__(self, chorus=ChorusSettings(bypass=True),
                 wave_shape='sine', t=None,f=440.0, max_vol=1.0, mono=True):
        self.t = t
        self.f = f
        note_multiple = 1.05946
        self.frequency_step = (note_multiple ** (1/30))
        self.wave_shape = wave_shape
        self.mono = mono
        self.max_vol_left = max_vol
        self.max_vol_right = max_vol
        self.sample_rate = 44100

        self.playing = False
        self.dry_signal = DrySignal(wave_shape=wave_shape, f=f, max_vol=self.max_vol_left,
                                              mono=mono, frequency_step=self.frequency_step)
        self.p = pyaudio.PyAudio()
        channel_count = 1 if mono else 2
        self.stream = self.p.open(format=pyaudio.paFloat32, channels=channel_count, rate=self.sample_rate, output=True)
        self.thread = None

        self.chorus = chorus
        self.__init__create_chorus_waves()

        self.play(t=t)

    def __init__create_chorus_waves(self):
        if self.chorus.bypass: return
        self.chorus.delay_f = self.chorus.convert_sec_to_f(self.chorus.delay_sec, self.f)
        self.chorus.depth_f = self.chorus.convert_sec_to_f(self.chorus.depth_sec, self.f)

        self.lower_chorus = {
            'initial_f': self.f - self.chorus.delay_f,
            'target_f': self.f - self.chorus.delay_f - self.chorus.depth_f,
            'decrease_f': False,
            'max_vol': self.max_vol_right
        }
        self.lower_chorus['signal'] = DrySignal(wave_shape=self.wave_shape, mono=self.mono,
                                                f=self.lower_chorus['initial_f'],
                                                max_vol=self.lower_chorus['max_vol'])
        self.lower_chorus['signal'].set_frequency(self.lower_chorus['target_f'])
        self.upper_chorus = {
            'initial_f': self.f + self.chorus.delay_f,
            'target_f': self.f + self.chorus.delay_f + self.chorus.delay_f,
            'decrease_f': True,
            'max_vol': self.max_vol_right
        }
        self.upper_chorus['signal'] = DrySignal(wave_shape=self.wave_shape, mono=self.mono,
                                                f=self.upper_chorus['initial_f'],
                                                max_vol=self.upper_chorus['max_vol'])
        self.upper_chorus['signal'].set_frequency(self.upper_chorus['target_f'])

    def _internal_play_loop(self, t=0.0):
        start_time = time.time()
        infinite_flag = True if t is None else False
        while (infinite_flag or time.time() - start_time < t) and self.playing:
            self.write_audio(start_time)

        self.dry_signal.set_volume(0, channel='mono')
        while self.dry_signal.volume_left != 0 and self.dry_signal.volume_right != 0:
            self.dry_signal.set_volume(0, channel='mono')
            self.write_audio(start_time)

    def write_audio(self, start_time):
        sample = self.dry_signal.receive_chunk()
        if (not self.chorus.bypass) and (time.time() - start_time > self.chorus.delay_sec):
            sample = self._internal_add_chorus(sample)
        print(sample)
        output_bytes = sample.tobytes()
        self.stream.write(output_bytes)


    def play(self, t=None):
        self.playing = False
        if self.thread and self.thread.is_alive():
            self.thread.join()

        self.playing = True
        self.dry_signal.set_volume(self.max_vol_left, channel='mono')
        self.thread = threading.Thread(target=self._internal_play_loop, kwargs={'t': t})
        self.thread.start()

    def set_frequency(self, frequency):
        self.f = frequency
        self.dry_signal.set_frequency(frequency)
        if not self.chorus.bypass:
            self.update_chorus_settings(chorus=self.chorus)
            self.set_chorus_frequency(self.lower_chorus, lower_flag=-1, direct=False)
            self.set_chorus_frequency(self.upper_chorus, lower_flag= 1, direct=False)

    def set_direct_frequency(self, frequency):
        self.f = frequency
        self.dry_signal.set_direct_frequency(frequency)
        if not self.chorus.bypass:
            self.update_chorus_settings(chorus=self.chorus)
            self.set_chorus_frequency(self.lower_chorus, lower_flag=-1, direct=True)
            self.set_chorus_frequency(self.upper_chorus, lower_flag= 1, direct=True)

    def set_chorus_frequency(self, signal, lower_flag, direct=False):
        decreasing_flag = -1 if signal['decrease_f'] else 1
        signal['initial_f'] = self.f + (self.chorus.delay_f * lower_flag)
        signal['target_f'] = signal['initial_f'] + (self.chorus.depth_f * decreasing_flag)

        if direct:
            signal['signal'].set_direct_frequency(signal['target_f'])
        else:
            signal['signal'].set_frequency(signal['target_f'], frequency_step=self.frequency_step)

    def set_volume(self, volume, channel='mono'):
        if self.mono or channel.lower() in ('left', 'mono'):
            self.max_vol_left = volume
            self.dry_signal.set_volume(self.max_vol_left, channel='left')
            if not self.chorus.bypass:
                self.lower_chorus['signal'].set_volume(self.max_vol_left, channel='left')
                self.upper_chorus['signal'].set_volume(self.max_vol_left, channel='left')

        if self.mono or channel.lower() in ('right', 'mono'):
            self.max_vol_right = volume
            self.dry_signal.set_volume(self.max_vol_right, channel='right')
            if not self.chorus.bypass:
                self.lower_chorus['signal'].set_volume(self.max_vol_right, channel='right')
                self.upper_chorus['signal'].set_volume(self.max_vol_right, channel='right')

    def update_chorus_settings(self, chorus):
        self.chorus = chorus
        self.chorus.delay_f = self.chorus.convert_sec_to_f(self.chorus.delay_sec, self.f)
        self.chorus.depth_f = self.chorus.convert_sec_to_f(self.chorus.depth_sec, self.f)

    def _internal_add_chorus(self, sample):
        self._internal_chorus_lfo()
        dry_gain = 1 - self.chorus.dry_wet
        wet_gain = self.chorus.dry_wet / 2
        sample = sample * dry_gain  # dry portion of the sample

        for signal in (self.lower_chorus, self.upper_chorus):
            chorus_signal = signal['signal'].receive_chunk() * wet_gain
            if len(chorus_signal) > len(sample):
                chorus_signal = chorus_signal[:len(sample)]
            while len(chorus_signal) < len(sample):
                chorus_signal = np.concatenate((chorus_signal, signal['signal'].get_next_sample() * wet_gain))
            sample = sample + chorus_signal

        return sample.astype(np.float32)

    def _internal_chorus_lfo(self):
        for signal in (self.lower_chorus, self.upper_chorus):
            self._internal_change_chorus_target_frequency(signal)

    def _internal_change_chorus_target_frequency(self, signal):
        lower_voice_flag = -1 if signal['initial_f'] < self.f else 1
        if signal['decrease_f'] and (signal['signal'].f <= signal['target_f']):
            self._internal_flip_chorus_direction(signal, lower_voice_flag, decrease_f=False)

        elif (not signal['decrease_f']) and signal['signal'].f >= signal['target_f']:
            self._internal_flip_chorus_direction(signal, lower_voice_flag, decrease_f=True)

    def _internal_flip_chorus_direction(self, signal, lower_voice_flag, decrease_f):
        subtract = -1 if decrease_f else 1
        signal['decrease_f'] = decrease_f
        signal['target_f'] = self.f + (self.chorus.delay_f * lower_voice_flag) + (self.chorus.depth_f * subtract)
        frequency_step_per_sec = (signal['target_f'] - signal['initial_f']) / (self.chorus.speed_sec / 4)
        frequency_step = abs(frequency_step_per_sec / signal['signal'].f)
        signal['signal'].set_frequency(signal['target_f'], linear=True, frequency_step=frequency_step)

    def pause(self):
        self.max_vol_left  = 0
        self.max_vol_right = 0
        self.dry_signal.set_volume(0, channel= 'mono')
        if not self.chorus.bypass:
            self.lower_chorus['signal'].set_volume(0, channel='mono')
            self.upper_chorus['signal'].set_volume(0, channel='mono')

        # remove previous thread
        self.playing = False
        time.sleep(.04)

    def stop(self):
        self.playing = False
        time.sleep(.2)  # make sure sound eases out
        self.thread.join()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

def main():
    chorus = ChorusSettings(bypass=True, depth=0, delay=0, dry_wet=0, speed=0.01)
    wave = Wave(chorus, f=800, wave_shape='triangle', max_vol=.5)
    time.sleep(1)
    chorus = ChorusSettings(bypass=False, depth=2.83, speed=0.13, delay=11.34, dry_wet=0.28)
    wave.update_chorus_settings(chorus)
    time.sleep(1)
    chorus = ChorusSettings(bypass=False, depth=2.8331251, speed=0.123142, delay=11.91827, dry_wet=0.282947)
    wave.update_chorus_settings(chorus)
    # time.sleep(1)
    # chorus = ChorusSettings.ChorusSettings(bypass=False, depth=0, delay=0)
    # wave.update_chorus_settings(chorus)
    # wave2 = Wave(chorus, wave_shape='triangle', max_vol=.25, f=450)
    # wave3 = Wave(chorus, wave_shape='triangle', max_vol=.25, f=460)


if __name__ == '__main__':
    main()