import numpy as np

class CreateWaveShape:
    def __init__(self, wave_shape, sample_rate):
        selectable_waves = {'sine':
                            (np.sin(2 * np.pi * np.arange(sample_rate) / sample_rate)).astype(np.float32),

                            'square':
                            np.concatenate((np.ones(sample_rate//2), np.zeros(sample_rate//2)))
                            }

        try:
            self.array = selectable_waves[wave_shape]
        except IndexError:
            print(f"{wave_shape} is not a valid wave_shape")