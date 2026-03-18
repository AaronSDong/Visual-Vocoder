import time
from pysinewave import SineWave

# Create a sine wave object with a starting pitch
# Pitch is a musical scale unit, where 9 is 440 Hz (A4)
sinewave = SineWave(pitch=9, pitch_per_second=10)

# Turn the sine wave on
sinewave.play()

# Keep playing for 2 seconds
time.sleep(2)

# Smoothly change the pitch to a lower note (-5, which is Middle C)
sinewave.set_pitch(-5)

# Keep playing for another 3 seconds while it transitions
time.sleep(30)

# Stop the sine wave
sinewave.stop()
