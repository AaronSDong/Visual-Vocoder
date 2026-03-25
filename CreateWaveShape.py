import numpy as np

class CreateWaveShape:
    def __init__(self, wave_shape, sample_rate):
        selectable_waves = {'sine':
                            (np.sin(2 * np.pi * np.arange(sample_rate) / sample_rate)).astype(np.float32),

                            'square':
                            np.concatenate((-np.ones(sample_rate//2), np.ones(sample_rate//2))),

                            # Noisy for some reason, check later
                            'triangle':
                                np.concatenate((np.linspace(-1, 1, sample_rate//2, endpoint=False),
                                                np.linspace(1, -1, sample_rate//2, endpoint=False)),),

                            # Noisy for some reason, check later
                            'saw':
                                np.linspace(-1, 1, sample_rate, endpoint=False)
                            }

        try:
            self.array = selectable_waves[wave_shape]
        except IndexError:
            print(f"{wave_shape} is not a valid wave_shape")

def main():
    wave = CreateWaveShape('triangle', 44100)
    print(wave.array)
    pass

if __name__ == '__main__':
    main()