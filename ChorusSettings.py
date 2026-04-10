from numpy import pi

class ChorusSettings:
    def __init__(self, bypass=True, delay=20, depth=5, speed=.4, dry_wet=.5):
        """
        General settings for chorus:
        Delay (ms):  5.0-50.0
        Depth (ms):  1.0-30.0
        Speed (Hz):  0.1-2.0
        Dry Wet:     0.0-1.0

        It is worth noting that small differences in ALL chorus effects are generally subtle.
        In order to really see if a feature is working the best method would be to test the max and mins of the plugin,
        or simply print out chorus frequency outputs to see the difference.
        """
        self.bypass = bypass
        self.delay_ms = delay
        self.depth_ms = depth
        self.speed_hz = speed
        self.dry_wet = dry_wet
        self.__init__change_units()

        self.delay_f = None
        self.depth_f = None

    def __init__change_units(self):
        self.delay_sec = self.delay_ms / 1000
        self.depth_sec = self.depth_ms / 1000
        self.speed_sec = 1 / self.speed_hz

    def convert_sec_to_f(self, factor_to_convert, f):
        new_voice_f = 1 / ((1 / f) - (factor_to_convert / (2*self.speed_sec*f)))
        return abs(new_voice_f - f)