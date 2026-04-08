class ChorusSettings:
    def __init__(self, bypass=True, delay=50, depth=50, speed=.5, dry_wet=.5):
        self.bypass = bypass
        self.delay_ms = delay
        self.depth_ms = depth
        self.speed_hz = speed
        self.dry_wet = dry_wet
        self.voice_separation = None
        self.__init__change_units()

    def __init__change_units(self):
        self.delay_sec = self.delay_ms / 1000
        self.depth_sec = self.depth_ms / 1000
        self.speed_sec = 1 / self.speed_hz

    def calculate_voice_separation(self, f):
        new_voice_location = 1 / ((1 / f) - (self.delay_sec / (2*self.speed_sec*f)))
        self.voice_separation = abs(new_voice_location - f)