import DrySignal
import time
import pyaudio
import threading
import numpy as np
import random

class Wave:
    def __init__(self, chorus=None, wave_shape='sine', t=None, f=440.0, max_vol=1.0, mono=True):
        self.t = t
        self.f = f
        self.wave_shape = wave_shape
        self.mono = mono
        self.chorus_dry_wet = chorus['dry_wet']  # in ratio from 0.0-1.0
        self.max_vol_left = max_vol
        self.max_vol_right = max_vol
        self.sample_rate = 44100

        self.playing = False
        self.signal = DrySignal.DrySignal(wave_shape=wave_shape, f=f, max_vol=self.max_vol_left,
                                          mono=mono)
        self.p = pyaudio.PyAudio()
        channel_count = 1 if mono else 2
        self.stream = self.p.open(format=pyaudio.paFloat32, channels=channel_count, rate=self.sample_rate, output=True)
        self.thread = None

        if chorus is None: chorus = {'bypass': True}
        self.chorus_bypass = chorus['bypass']
        self.chorus_delay = 0.0
        self.chorus_speed = 0.0
        self.chorus_frequency_depth = 0.0
        self.chorus_voice_separation = 0.0
        self.__init__create_chorus_waves(chorus)

        self.play(t=t)

    def __init__create_chorus_waves(self, chorus):
        if chorus['bypass']: return

        self.update_chorus_variables(chorus)
        self.lower_chorus_voice = {
            'initial_f': self.f - self.chorus_voice_separation,
            'target_f': self.f - self.chorus_voice_separation -
                        (self.chorus_frequency_depth*random.uniform(0.9, 1.1)),
            'decrease_f': True,
            'max_vol': self.max_vol_right
        }
        self.lower_chorus_voice['signal'] = DrySignal.DrySignal(wave_shape=self.wave_shape, mono=self.mono,
                                                                f=self.lower_chorus_voice['initial_f'],
                                                                max_vol=self.lower_chorus_voice['max_vol'])
        self.lower_chorus_voice['signal'].set_frequency(self.lower_chorus_voice['target_f'])
        self.upper_chorus_voice = {
            'initial_f': self.f + self.chorus_voice_separation,
            'target_f': self.f + self.chorus_voice_separation +
                        (self.chorus_frequency_depth * random.uniform(0.9, 1.1)),
            'decrease_f': False,
            'max_vol': self.max_vol_right
        }
        self.upper_chorus_voice['signal'] = DrySignal.DrySignal(wave_shape=self.wave_shape, mono=self.mono,
                                                                f=self.upper_chorus_voice['initial_f'],
                                                                max_vol=self.upper_chorus_voice['max_vol'])
        self.upper_chorus_voice['signal'].set_frequency(self.upper_chorus_voice['target_f'])

    def update_chorus_variables(self, chorus):
        self.chorus_delay = chorus['delay'] / 1000  # in secs
        self.chorus_speed = 1 / chorus['speed']  # Hz to sec
        self.chorus_frequency_depth = chorus['depth'] / 1000  # in secs
        new_voice_location = 1 / ((1 / self.f) - (self.chorus_delay / (2*self.chorus_speed*self.f)))
        self.chorus_voice_separation = abs(new_voice_location - self.f)

    def play_loop(self, t=0.0):
        start_time = time.time()
        infinite_flag = True if t is None else False
        while (infinite_flag or time.time() - start_time < t) and self.playing:
            sample = self.signal.receive_chunk()
            if not self.chorus_bypass and time.time() - start_time > self.chorus_delay:
                sample = self.add_chorus(sample)
            output_bytes = sample.tobytes()
            self.stream.write(output_bytes)

        self.signal.set_volume(0, channel='mono')
        while self.signal.volume_left != 0 and self.signal.volume_right != 0:
            self.signal.set_volume(0, channel= 'left')
            self.signal.set_volume(0, channel='right')
            sample = self.signal.receive_chunk()
            # Chorus effect here
            output_bytes = sample.tobytes()
            self.stream.write(output_bytes)

    def play(self, t=None):
        self.playing = False
        if self.thread and self.thread.is_alive():
            self.thread.join()   # wait for old thread to fully stop

        self.playing = True
        self.signal.set_volume(self.max_vol_left, channel='left')
        self.signal.set_volume(self.max_vol_right, channel='right')
        self.thread = threading.Thread(target=self.play_loop, kwargs={'t': t})
        self.thread.start()

    def set_frequency(self, frequency):
        self.f = frequency
        self.signal.set_frequency(frequency)

    def set_direct_frequency(self, frequency):
        self.f = frequency
        self.signal.set_direct_frequency(frequency)

    def set_volume(self, volume, channel='mono'):
        if self.mono or channel.lower() in ('left', 'mono'):
            self.max_vol_left = volume
            for signal in (self.signal, self.lower_chorus_voice, self.upper_chorus_voice):
                if signal is not None: signal.set_volume(self.max_vol_left, channel= 'left')

        if self.mono or channel.lower() in ('right', 'mono'):
            self.max_vol_right = volume
            for signal in (self.signal, self.lower_chorus_voice, self.upper_chorus_voice):
                if signal is None: continue
                signal.set_volume(self.max_vol_right, channel= 'right')

    def add_chorus(self, sample):
        #self.update_chorus()
        dry_gain = 1 - self.chorus_dry_wet
        wet_gain = self.chorus_dry_wet / 2
        sample = sample * dry_gain  # dry portion of the sample
        print('dry signal ' + str(self.signal.next_sample))

        for signal in (self.lower_chorus_voice, self.upper_chorus_voice):
            print('chorus signal ' + str(signal['signal'].next_sample))
            chorus_signal = signal['signal'].receive_chunk() * wet_gain
            if len(chorus_signal) > len(sample):
                chorus_signal = chorus_signal[:len(sample)]
            while len(chorus_signal) < len(sample):
                chorus_signal = np.concatenate((chorus_signal, signal['signal'].get_next_sample() * wet_gain))
            sample = sample + chorus_signal
        return sample.astype('float32')

    def update_chorus(self):
        for signal in (self.lower_chorus_voice, self.upper_chorus_voice):
            self.change_chorus_target_frequency(signal)

    def change_chorus_target_frequency(self, signal):
        lower_voice_flag = -1 if signal['initial_f'] < self.f else 1
        if signal['decrease_f'] and signal['signal'].f <= signal['target_f']:
            signal['decrease_f'] = False
            signal['target_f'] = (self.f + (self.chorus_voice_separation*lower_voice_flag) +
                                 (self.chorus_frequency_depth*random.uniform(0.9, 1.1)))
            signal['signal'].set_frequency(signal['target_f'])

        elif not signal['decrease_f'] and signal['signal'].f >= signal['target_f']:
            signal['decrease_f'] = True
            signal['target_f'] = (self.f + (self.chorus_voice_separation*lower_voice_flag) -
                                 (self.chorus_frequency_depth*random.uniform(0.9, 1.1)))
            signal['signal'].set_frequency(signal['target_f'])

    def pause(self):
        self.max_vol_left  = 0
        self.max_vol_right = 0
        for signal in (self.signal, self.lower_chorus_voice, self.upper_chorus_voice):
            if signal is None: continue
            signal.set_volume(0, channel= 'left')
            signal.set_volume(0, channel='right')

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

    chorus = {
        'bypass': False,
        'delay': 50,
        'depth': 50,
        'speed': .5,
        'dry_wet': 1
    }
    wave = Wave(chorus, wave_shape='triangle', max_vol=1)
    # wave2 = Wave(chorus, wave_shape='triangle', max_vol=.5, f=445)
    # wave3 = Wave(chorus, wave_shape='triangle', max_vol=.5, f=450)


if __name__ == '__main__':
    main()