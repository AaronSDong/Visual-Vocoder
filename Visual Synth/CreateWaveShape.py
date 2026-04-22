import numpy as np
from SettingsScript import load_settings

class CreateWaveShape:
    def __init__(self, wave_shape, sample_rate):
        settings = load_settings()
        selectable_waves = {'sine':
                            (np.sin(2 * np.pi * np.arange(sample_rate) / sample_rate)).astype(np.float32),

                            'square':
                            np.concatenate((np.ones(sample_rate//2), -np.ones(sample_rate//2))),

                            'triangle':
                            np.concatenate((np.linspace(-1, 1, sample_rate//2, endpoint=False),
                                            np.linspace(1, -1, sample_rate//2, endpoint=False)),),

                            'saw':
                            np.linspace(-1, 1, sample_rate, endpoint=False),

                            'custom':
                            settings['custom_wave'] if settings['custom_wave'] != []
                            else (np.sin(2 * np.pi * np.arange(sample_rate) / sample_rate)).astype(np.float32),
                            }

        try:
            self.array = selectable_waves[wave_shape]
        except IndexError:
            print(f"{wave_shape} is not a valid wave_shape")

def main():
    wave = CreateWaveShape('triangle', 44100)
    print(wave.array)

if __name__ == '__main__':
    main()