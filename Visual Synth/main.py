"""
Project Notes:
Most of the effort spent on this project was focused on the auditory aspect of it (specifically, the WaveGroup class
and anything deeper inside of it). Much care was used to ensure that audio played would not 'clip,' as these bugs are
very common. Each of the wave classes were written to also operate independently outside of this specific project,
and as such main() functions were written at the bottom of most of them to demonstrate that. Outside the vocoder,
all audio processing was done manually with only the use of pyaudio to play the signals.
Files to look at: 'WaveGroup.py' --> 'Wave.py' --> 'DrySignal.py'

To get an indepth description of the project, please see the 'How To Play' section of my program. In short, curling your
fingers will result in the synth playing a tone, with hand movements controlling certain parameters. To see how fingers
are detected, please see 'Camera.py,' specifically from line 60 down.

All UI elements are contained within 'main.py'

Music, art, and sfx assets were created by me.
"""

from cmu_graphics import *
from Camera import camera
from CameraVocoder import camera as cameraVocoder
from SettingsScript import *
from CreateWaveShape import CreateWaveShape
from random import randint

class Slider:
    def __init__(self, setting, setting_value, range_of_values, x_value, y_range):
        self.clicked_on = False
        self.setting = setting
        self.setting_value = setting_value  # UPDATE, get settings from a settings file
        self.range_of_values = range_of_values  # takes tuple

        self.x_value = int(x_value)
        self.y_range = (int(y_range[0]), int(y_range[1]))  # takes tuple
        range_length = self.range_of_values[1] - self.range_of_values[0]
        value_proportion = (self.setting_value - self.range_of_values[0]) / range_length
        y_length = self.y_range[1] - self.y_range[0]
        self.y_value = int(value_proportion * y_length + y_range[0])

    def convert_pixels_to_value(self):
        y_length = self.y_range[1] - self.y_range[0]
        y_proportion = (self.y_value - self.y_range[0]) / y_length
        range_length = self.range_of_values[1] - self.range_of_values[0]

        self.setting_value = pythonRound((range_length * y_proportion) + self.range_of_values[0], 2)
        update_settings_file(self.setting, self.setting_value)

    def update_y_value(self, y):
        if   y < self.y_range[0]: self.y_value = self.y_range[0]
        elif y > self.y_range[1]: self.y_value = self.y_range[1]
        else: self.y_value = y
        self.convert_pixels_to_value()

def onAppStart(app):
    app.width = 1000
    app.height = 800

    settings = load_settings()
    app.enable_vocoder = settings['enable_vocoder']
    app.enable_mono = settings['enable_mono']

    app.play_sound_cooldown = 10
    app.bg_music = Sound('assets\\bgMusic.mp3')
    app.font = 'Pixelated Elegance'
    app.text_color = rgb(180, 20, 229)
    app.neon_green = rgb(57, 255, 20)
    app.hovered_text_color = rgb(255, 0, 255)

    app.screen = 'title_screen'
    app.how_to_play_page = 0
    app.how_to_play_page_count = 7
    load_buttons(app)
    load_sliders(app)
    load_edit_wave_grid(app)
    update_edit_wave_grid(app)

def load_buttons(app):
    assets_folder = 'assets\\'
    settings = load_settings()

    if not hasattr(app, 'button_play'): app.button_play = {}  # idea taken from AI
    app.button_play['cx'] = app.width//2 - 100
    app.button_play['cy'] = int(app.height * .45)
    app.button_play['w'] = 200
    app.button_play['h'] = 100
    app.button_play['image_off'] = assets_folder + 'Play Button.png'
    app.button_play['image_on'] = assets_folder + 'Play Button On.png'
    app.button_play['hovered'] = app.button_play.get('hovered', False)

    if not hasattr(app, 'button_menu'): app.button_menu = {}
    app.button_menu['cx'] = app.width // 2 - 100
    app.button_menu['cy'] = int(app.height * .625)
    app.button_menu['w'] = 200
    app.button_menu['h'] = 100
    app.button_menu['image_off'] = assets_folder + 'Menu Button.png'
    app.button_menu['image_on'] = assets_folder + 'Menu Button On.png'
    app.button_menu['hovered'] = app.button_menu.get('hovered', False)

    if not hasattr(app, 'button_how_to_play'): app.button_how_to_play = {}
    app.button_how_to_play['cx'] = app.width // 2 - 100
    app.button_how_to_play['cy'] = int(app.height * .8)
    app.button_how_to_play['w'] = 200
    app.button_how_to_play['h'] = 100
    app.button_how_to_play['image_off'] = assets_folder + 'How To Play Button.png'
    app.button_how_to_play['image_on'] = assets_folder + 'How To Play Button On.png'
    app.button_how_to_play['hovered'] = app.button_how_to_play.get('hovered', False)

    if not hasattr(app, 'button_exit'): app.button_exit = {}
    app.button_exit['cx'] = app.width - 90
    app.button_exit['cy'] = 30
    app.button_exit['w'] = 50
    app.button_exit['h'] = 50
    app.button_exit['image_off'] = assets_folder + 'Exit Button.png'
    app.button_exit['image_on'] = assets_folder + 'Exit Button On.png'
    app.button_exit['hovered'] = app.button_exit.get('hovered', False)

    if not hasattr(app, 'button_left'): app.button_left = {}
    app.button_left['cx'] = app.width // 2 - 70
    app.button_left['cy'] = app.height - 75
    app.button_left['w'] = 50
    app.button_left['h'] = 50
    app.button_left['image_off'] = assets_folder + 'Left Arrow.png'
    app.button_left['image_on'] = assets_folder + 'Left Arrow On.png'
    app.button_left['hovered'] = app.button_left.get('hovered', False)

    if not hasattr(app, 'button_right'): app.button_right = {}
    app.button_right['cx'] = app.width // 2 + 20
    app.button_right['cy'] = app.height - 75
    app.button_right['w'] = 50
    app.button_right['h'] = 50
    app.button_right['image_off'] = assets_folder + 'Right Arrow.png'
    app.button_right['image_on'] = assets_folder + 'Right Arrow On.png'
    app.button_right['hovered'] = app.button_right.get('hovered', False)

    if not hasattr(app, 'button_chorus'): app.button_chorus = {}
    app.button_chorus['cx'] = int(app.width * .25 - 136/2)
    app.button_chorus['cy'] = app.height // 4 - 12
    app.button_chorus['w'] = 140
    app.button_chorus['h'] = 70
    app.button_chorus['text'] = 'Chorus\nEffect'
    app.button_chorus['size'] = 30
    app.button_chorus['color'] = app.text_color
    app.button_chorus['hovered'] = app.button_chorus.get('hovered', False)

    if not hasattr(app, 'button_test_wave'): app.button_test_wave = {}
    app.button_test_wave['cx'] = app.width // 2 - (210//2)
    app.button_test_wave['cy'] = 3*app.height // 4
    app.button_test_wave['w'] = 210
    app.button_test_wave['h'] = 25
    app.button_test_wave['text'] = 'Test Wave'
    app.button_test_wave['size'] = 30
    app.button_test_wave['color'] = app.button_test_wave.get('color', app.text_color)
    app.button_test_wave['hovered'] = app.button_test_wave.get('hovered', False)

    if not hasattr(app, 'button_choose_key'): app.button_choose_key = {}
    app.button_choose_key['cx'] = int(app.width * .5 - 76 / 2)
    app.button_choose_key['cy'] = app.height // 4 - 12
    app.button_choose_key['w'] = 74
    app.button_choose_key['h'] = 28
    app.button_choose_key['text'] = 'Key'
    app.button_choose_key['size'] = 30
    app.button_choose_key['color'] = app.text_color
    app.button_choose_key['hovered'] = app.button_choose_key.get('hovered', False)

    if not hasattr(app, 'button_decrease_1'): app.button_decrease_1 = {}
    app.button_decrease_1['cx'] = app.width // 2 - 200
    app.button_decrease_1['cy'] = app.height // 2 + 150
    app.button_decrease_1['w'] = 150
    app.button_decrease_1['h'] = 150
    app.button_decrease_1['image_off'] = assets_folder + 'Left Arrow.png'
    app.button_decrease_1['image_on'] = assets_folder + 'Left Arrow On.png'
    app.button_decrease_1['hovered'] = app.button_decrease_1.get('hovered', False)

    if not hasattr(app, 'button_increase_1'): app.button_increase_1 = {}
    app.button_increase_1['cx'] = app.width // 2 + 50
    app.button_increase_1['cy'] = app.height // 2 + 150
    app.button_increase_1['w'] = 150
    app.button_increase_1['h'] = 150
    app.button_increase_1['image_off'] = assets_folder + 'Right Arrow.png'
    app.button_increase_1['image_on'] = assets_folder + 'Right Arrow On.png'
    app.button_increase_1['hovered'] = app.button_increase_1.get('hovered', False)

    if not hasattr(app, 'button_choose_scale'): app.button_choose_scale = {}
    app.button_choose_scale['cx'] = int(app.width * .75 - 102/2)
    app.button_choose_scale['cy'] = app.height // 4 - 12
    app.button_choose_scale['w'] = 120
    app.button_choose_scale['h'] = 28
    app.button_choose_scale['text'] = 'Scale'
    app.button_choose_scale['size'] = 30
    app.button_choose_scale['color'] = app.text_color
    app.button_choose_scale['hovered'] = app.button_choose_scale.get('hovered', False)

    if not hasattr(app, 'button_mono'): app.button_mono = {}
    app.button_mono['cx'] = int(app.width * .25 - 100/2)
    app.button_mono['cy'] = int(app.height * .5) - 12
    app.button_mono['w'] = 100
    app.button_mono['h'] = 28
    app.button_mono['text'] = 'Mono'
    app.button_mono['size'] = 30
    app.button_mono['color'] = app.text_color
    app.button_mono['hovered'] = app.button_mono.get('hovered', False)

    if not hasattr(app, 'button_enable_mono_on'): app.button_enable_mono_on = {}
    app.button_enable_mono_on['cx'] = (app.width // 2 + 100) - 40 // 2
    app.button_enable_mono_on['cy'] = (app.height // 2) - 25 // 2
    app.button_enable_mono_on['w'] = 50
    app.button_enable_mono_on['h'] = 25
    app.button_enable_mono_on['text'] = 'On'
    app.button_enable_mono_on['size'] = 30
    app.button_enable_mono_on['color'] = app.button_enable_mono_on.get('color', app.text_color)
    app.button_enable_mono_on['hovered'] = app.button_enable_mono_on.get('hovered', False)

    if not hasattr(app, 'button_enable_mono_off'): app.button_enable_mono_off = {}
    app.button_enable_mono_off['cx'] = (app.width // 2 + 100) - 60 // 2
    app.button_enable_mono_off['cy'] = (app.height // 2) - 25 // 2
    app.button_enable_mono_off['w'] = 70
    app.button_enable_mono_off['h'] = 25
    app.button_enable_mono_off['text'] = 'Off'
    app.button_enable_mono_off['size'] = 30
    app.button_enable_mono_off['color'] = app.button_enable_mono_off.get('color', app.text_color)
    app.button_enable_mono_off['hovered'] = app.button_enable_mono_off.get('hovered', False)

    if not hasattr(app, 'button_choose_wave'): app.button_choose_wave = {}
    app.button_choose_wave['cx'] = int(app.width * .5 - 111 / 2)
    app.button_choose_wave['cy'] = int(app.height * .5) - 12
    app.button_choose_wave['w'] = 124
    app.button_choose_wave['h'] = 76
    app.button_choose_wave['text'] = 'Wave\nShape'
    app.button_choose_wave['size'] = 30
    app.button_choose_wave['color'] = app.text_color
    app.button_choose_wave['hovered'] = app.button_choose_wave.get('hovered', False)

    if not hasattr(app, 'button_edit_custom_wave'): app.button_edit_custom_wave = {}
    app.button_edit_custom_wave['cx'] = app.width // 2 - 123
    app.button_edit_custom_wave['cy'] = int(app.height * .57) - 8
    app.button_edit_custom_wave['w'] = 246
    app.button_edit_custom_wave['h'] = 22
    app.button_edit_custom_wave['text'] = 'Edit Custom Wave'
    app.button_edit_custom_wave['size'] = 20
    app.button_edit_custom_wave['color'] = app.button_edit_custom_wave.get('color', app.text_color)
    app.button_edit_custom_wave['hovered'] = app.button_edit_custom_wave.get('hovered', False)

    if not hasattr(app, 'button_decrease_2'): app.button_decrease_2 = {}
    app.button_decrease_2['cx'] = int(app.width*.25 - 75)
    app.button_decrease_2['cy'] = int(app.height * .88)
    app.button_decrease_2['w'] = 50
    app.button_decrease_2['h'] = 50
    app.button_decrease_2['image_off'] = assets_folder + 'Left Arrow.png'
    app.button_decrease_2['image_on'] = assets_folder + 'Left Arrow On.png'
    app.button_decrease_2['hovered'] = app.button_decrease_2.get('hovered', False)

    if not hasattr(app, 'button_increase_2'): app.button_increase_2 = {}
    app.button_increase_2['cx'] = int(app.width*.25 + 25)
    app.button_increase_2['cy'] = int(app.height * .88)
    app.button_increase_2['w'] = 50
    app.button_increase_2['h'] = 50
    app.button_increase_2['image_off'] = assets_folder + 'Right Arrow.png'
    app.button_increase_2['image_on'] = assets_folder + 'Right Arrow On.png'
    app.button_increase_2['hovered'] = app.button_increase_2.get('hovered', False)

    if not hasattr(app, 'button_decrease_3'): app.button_decrease_3 = {}
    app.button_decrease_3['cx'] = int(app.width*.75 - 75)
    app.button_decrease_3['cy'] = int(app.height * .88)
    app.button_decrease_3['w'] = 50
    app.button_decrease_3['h'] = 50
    app.button_decrease_3['image_off'] = assets_folder + 'Left Arrow.png'
    app.button_decrease_3['image_on'] = assets_folder + 'Left Arrow On.png'
    app.button_decrease_3['hovered'] = app.button_decrease_3.get('hovered', False)

    if not hasattr(app, 'button_increase_3'): app.button_increase_3 = {}
    app.button_increase_3['cx'] = int(app.width*.75 + 25)
    app.button_increase_3['cy'] = int(app.height * .88)
    app.button_increase_3['w'] = 50
    app.button_increase_3['h'] = 50
    app.button_increase_3['image_off'] = assets_folder + 'Right Arrow.png'
    app.button_increase_3['image_on'] = assets_folder + 'Right Arrow On.png'
    app.button_increase_3['hovered'] = app.button_increase_3.get('hovered', False)

    if not hasattr(app, 'button_reset_custom_wave'): app.button_reset_custom_wave = {}
    app.button_reset_custom_wave['cx'] = app.width - 204
    app.button_reset_custom_wave['cy'] = app.height - 26
    app.button_reset_custom_wave['w'] = 199
    app.button_reset_custom_wave['h'] = 28
    app.button_reset_custom_wave['text'] = 'Reset Custom Wave'
    app.button_reset_custom_wave['size'] = 15
    app.button_reset_custom_wave['color'] = app.text_color
    app.button_reset_custom_wave['hovered'] = app.button_reset_custom_wave.get('hovered', False)

    if not hasattr(app, 'button_vocoder'): app.button_vocoder = {}
    app.button_vocoder['cx'] = int(app.width * .75 - 156/2)
    app.button_vocoder['cy'] = int(app.height * .5) - 12
    app.button_vocoder['w'] = 152
    app.button_vocoder['h'] = 28
    app.button_vocoder['text'] = 'Vocoder'
    app.button_vocoder['size'] = 30
    app.button_vocoder['color'] = app.text_color
    app.button_vocoder['hovered'] = app.button_vocoder.get('hovered', False)

    if not hasattr(app, 'button_test_vocoder'): app.button_test_vocoder = {}
    app.button_test_vocoder['cx'] = app.width // 2 - (270//2)
    app.button_test_vocoder['cy'] = 3*app.height // 4
    app.button_test_vocoder['w'] = 270
    app.button_test_vocoder['h'] = 25
    app.button_test_vocoder['text'] = 'Test Vocoder'
    app.button_test_vocoder['size'] = 30
    app.button_test_vocoder['color'] = app.button_test_vocoder.get('color', app.text_color)
    app.button_test_vocoder['hovered'] = app.button_test_vocoder.get('hovered', False)

    if not hasattr(app, 'button_enable_vocoder_on'): app.button_enable_vocoder_on = {}
    app.button_enable_vocoder_on['cx'] = (app.width // 2 + 100) - 40//2
    app.button_enable_vocoder_on['cy'] = (app.height // 2) - 25//2
    app.button_enable_vocoder_on['w'] = 50
    app.button_enable_vocoder_on['h'] = 25
    app.button_enable_vocoder_on['text'] = 'On'
    app.button_enable_vocoder_on['size'] = 30
    app.button_enable_vocoder_on['color'] = app.button_enable_vocoder_on.get('color', app.text_color)
    app.button_enable_vocoder_on['hovered'] = app.button_enable_vocoder_on.get('hovered', False)

    if not hasattr(app, 'button_enable_vocoder_off'): app.button_enable_vocoder_off = {}
    app.button_enable_vocoder_off['cx'] = (app.width // 2 + 100) - 60//2
    app.button_enable_vocoder_off['cy'] = (app.height // 2) - 25//2
    app.button_enable_vocoder_off['w'] = 70
    app.button_enable_vocoder_off['h'] = 25
    app.button_enable_vocoder_off['text'] = 'Off'
    app.button_enable_vocoder_off['size'] = 30
    app.button_enable_vocoder_off['color'] = app.button_enable_vocoder_off.get('color', app.text_color)
    app.button_enable_vocoder_off['hovered'] = app.button_enable_vocoder_off.get('hovered', False)

    if not hasattr(app, 'button_reset_to_defaults'): app.button_reset_to_defaults = {}
    app.button_reset_to_defaults['cx'] = app.width - 194
    app.button_reset_to_defaults['cy'] = app.height - 26
    app.button_reset_to_defaults['w'] = 190
    app.button_reset_to_defaults['h'] = 28
    app.button_reset_to_defaults['text'] = 'Reset To Defaults'
    app.button_reset_to_defaults['size'] = 15
    app.button_reset_to_defaults['color'] = app.text_color
    app.button_reset_to_defaults['hovered'] = app.button_reset_to_defaults.get('hovered', False)

    if not hasattr(app, 'button_secret_music'): app.button_secret_music = {}
    app.button_secret_music['cx'] = 10
    app.button_secret_music['cy'] = app.height - 26
    app.button_secret_music['w'] = 140
    app.button_secret_music['h'] = 28
    app.button_secret_music['text'] = 'Secret Music'
    app.button_secret_music['size'] = 15
    app.button_secret_music['color'] = app.button_secret_music.get(app.text_color, None)
    app.button_secret_music['hovered'] = app.button_secret_music.get('hovered', False)

    # if statements by AI
    app.button_list_title_screen =     [app.button_play, app.button_menu, app.button_how_to_play]
    app.button_list_menu =             [app.button_exit, app.button_chorus, app.button_choose_key,
                                        app.button_choose_scale, app.button_mono, app.button_choose_wave,
                                        app.button_vocoder, app.button_reset_to_defaults, app.button_secret_music]
    app.button_list_chorus_effect =    [app.button_exit, app.button_test_wave]
    app.button_list_key =              [app.button_exit, app.button_increase_1, app.button_decrease_1]
    app.button_list_scale =            [app.button_exit, app.button_increase_1, app.button_decrease_1]
    app.button_list_mono =             [app.button_exit,
                                        app.button_enable_mono_on if app.enable_mono else app.button_enable_mono_off]
    app.button_list_wave =             [app.button_exit, app.button_increase_1, app.button_decrease_1]
    app.button_list_edit_custom_wave = [app.button_exit, app.button_increase_2, app.button_decrease_2,
                                        app.button_increase_3, app.button_decrease_3, app.button_reset_custom_wave]
    app.button_list_vocoder =          [app.button_exit, app.button_test_vocoder,
                                        app.button_enable_vocoder_on if app.enable_vocoder
                                        else app.button_enable_vocoder_off]
    app.button_list_how_to_play =      [app.button_exit, app.button_right, app.button_left]

    if settings['wave_shape'] == 'custom': app.button_list_wave.append(app.button_edit_custom_wave)

def load_sliders(app):
    app.slider_size = 30
    settings = load_settings()
    chorus_slider_y_range = (int(app.height * .45) - 90, int(app.height * .45) + 90)  # Taken from the pedal size

    chorus_delay_slider =   Slider('chorus_delay', settings['chorus_delay'], (5, 50),
                                   app.width//2 -  70, chorus_slider_y_range)
    chorus_depth_slider =   Slider('chorus_depth', settings['chorus_depth'], (1, 30),
                                   app.width//2 +  20, chorus_slider_y_range)
    chorus_speed_slider =   Slider('chorus_speed', settings['chorus_speed'], (.1, 2),
                                   app.width//2 + 110, chorus_slider_y_range)
    chorus_dry_wet_slider = Slider('chorus_dry_wet', settings['chorus_dry_wet'], (0, 1),
                                   app.width//2 + 200, chorus_slider_y_range)

    app.chorus_sliders = [chorus_delay_slider, chorus_depth_slider, chorus_speed_slider, chorus_dry_wet_slider]

def load_edit_wave_grid(app):
    app.edit_wave_grid_rows = 3
    app.edit_wave_grid_cols = 6
    app.edit_wave_curr_line = []

def update_edit_wave_grid(app):
    app.edit_wave_grid_width = int(app.width * .8)
    app.edit_wave_grid_height = int(app.height * .4)
    app.edit_wave_grid_left = int(app.width * .1)
    app.edit_wave_grid_top = int(app.height * .3)

    settings = load_settings()
    if settings['custom_wave'] == []:
        app.custom_wave = CreateWaveShape('sine', 44100).array
    else:
        app.custom_wave = settings['custom_wave']
        app.custom_wave = np.array(app.custom_wave)

def redrawAll(app):
    match app.screen:
        case 'title_screen':     draw_title_screen(app)
        case 'menu_screen':      draw_menu_screen(app)
        case 'chorus_effect':    draw_chorus_effect(app)
        case 'choose_key':       draw_choose_key(app)
        case 'choose_scale':     draw_choose_scale(app)
        case 'mono':             draw_mono(app)
        case 'choose_wave':      draw_choose_wave(app)
        case 'edit_custom_wave': draw_edit_custom_wave(app)
        case 'vocoder':          draw_vocoder(app)
        case 'how_to_play':      draw_how_to_play(app)

def draw_title_screen(app):
    draw_background(app)
    # drawLabel('Visual Synthesizer!', app.width // 2, app.height // 4, font=app.font, size=40, fill='magenta')
    for button in app.button_list_title_screen:
        draw_button(app, button)

def draw_menu_screen(app):
    draw_background(app)
    drawLabel('Menu', app.width//2, 100, font=app.font, size=60, fill=app.text_color)
    for button in app.button_list_menu:
        draw_button(app, button)

def draw_chorus_effect(app):
    draw_background(app)
    drawLabel('Chorus Effect', app.width//2, 100, font=app.font, size=60, fill=app.text_color)
    drawImage('Assets\\Menu Button.png', app.width//2, int(app.height * .45), width=600, height=300, align='center')
    for button in app.button_list_chorus_effect:
        draw_button(app, button)

    for slider in app.chorus_sliders:
        drawRect(slider.x_value, slider.y_value, app.slider_size, app.slider_size, fill='white', align='center')

def draw_choose_key(app):
    draw_background(app)
    drawLabel('Choose Key', app.width//2, 100, font=app.font, size=60, fill=app.text_color)

    settings = load_settings()
    drawLabel(settings['key'], app.width//2, int(app.height*.4), font=app.font, size=80, fill=app.text_color)

    for button in app.button_list_key:
        draw_button(app, button)

def draw_choose_scale(app):
    draw_background(app)
    drawLabel('Choose Scale', app.width//2, 100, font=app.font, size=60, fill=app.text_color)

    settings = load_settings()
    drawLabel(settings['scale'], app.width//2, int(app.height*.4), font=app.font, size=50, fill=app.text_color)

    for button in app.button_list_key:
        draw_button(app, button)

def draw_mono(app):
    # This function, along with anything relating to draw_mono, was taken from AI (prompted to copy my code)
    draw_background(app)
    drawLabel('Mono', app.width//2, 100, font=app.font, size=60, fill=app.text_color)
    drawLabel('Enable:', app.width//2 - 100, app.height//2, font=app.font, size=40, fill=app.text_color)

    for button in app.button_list_mono:
        draw_button(app, button)

def draw_choose_wave(app):
    # This function, along with anything relating to draw_choose_wave, was taken from AI (prompted to copy my code)
    draw_background(app)
    drawLabel('Choose Wave', app.width//2, 100, font=app.font, size=60, fill=app.text_color)

    settings = load_settings()
    drawLabel(settings['wave_shape'], app.width//2, int(app.height*.4), font=app.font, size=50, fill=app.text_color)

    for button in app.button_list_wave:
        draw_button(app, button)

def draw_edit_custom_wave(app):
    draw_background(app)
    drawLabel('Wave Editor', app.width//2, 100, font=app.font, size=60, fill=app.text_color)
    for button in app.button_list_edit_custom_wave:
        draw_button(app, button)

    # Grid incrementors
    drawLabel(f'Grid X: {app.edit_wave_grid_cols}', int(app.width * .25), int(app.height * .84),
              font=app.font, size=30, fill=app.text_color)
    drawLabel(f'Grid Y: {app.edit_wave_grid_rows}', int(app.width * .75), int(app.height * .84),
              font=app.font, size=30, fill=app.text_color)

    # Grid variables
    grid_width = app.edit_wave_grid_width
    grid_height = app.edit_wave_grid_height
    grid_left = app.edit_wave_grid_left
    grid_top = app.edit_wave_grid_top

    # Cell size
    cell_width, cell_height, circle_size = get_cell_size(app)

    # Draw boarder
    drawRect(grid_left-1, grid_top-1, grid_width+2, grid_height+2, fill=None, border='black', borderWidth=1)

    # Draw cell
    for row in range(app.edit_wave_grid_rows):
        for col in range(app.edit_wave_grid_cols):
            cell_left = grid_left + (col * cell_width)
            cell_top = grid_top + (row * cell_height)
            drawRect(cell_left, cell_top, cell_width, cell_height, fill=None, border='grey', borderWidth=1)

    # Draw grey circles
    for row in range(app.edit_wave_grid_rows + 1):
        for col in range(app.edit_wave_grid_cols + 1):
            cell_left = grid_left + (col * cell_width)
            cell_top = grid_top + (row * cell_height)
            drawCircle(cell_left, cell_top, circle_size, fill='grey', opacity=50)

    # Draw current line
    if app.edit_wave_curr_line != []:
        drawLine(*app.edit_wave_curr_line, fill='white', opacity=80, lineWidth=5)

    # Draw all points connected
    step_size = 100
    sample_rate = len(app.custom_wave)
    for i in range(0, len(app.custom_wave) - step_size, step_size):
        # Convert custom wave values to pixels
        x0 = ((i)           * (1/sample_rate) * app.edit_wave_grid_width) + app.edit_wave_grid_left
        x1 = ((i+step_size) * (1/sample_rate) * app.edit_wave_grid_width) + app.edit_wave_grid_left
        y0 = (((1 - app.custom_wave[i]) / 2)           * app.edit_wave_grid_height) + app.edit_wave_grid_top
        y1 = (((1 - app.custom_wave[i+step_size]) / 2) * app.edit_wave_grid_height) + app.edit_wave_grid_top
        x0, x1, y0, y1 = pythonRound(x0), pythonRound(x1), pythonRound(y0), pythonRound(y1)
        drawLine(x0, y0, x1, y1, fill='purple', lineWidth=3)

def get_cell_size(app):
    cell_width = app.edit_wave_grid_width / app.edit_wave_grid_cols
    cell_height = app.edit_wave_grid_height / app.edit_wave_grid_rows
    circle_size = min(cell_width, cell_height) * .25

    return cell_width, cell_height, circle_size

def draw_vocoder(app):
    draw_background(app)
    drawLabel('Vocoder', app.width//2, 100, font=app.font, size=60, fill=app.text_color)
    drawLabel('Enable:', app.width//2 - 100, app.height//2, font=app.font, size=40, fill=app.text_color)
    drawLabel('*Note: enabling the vocoder will', 10, app.height-40,
              font=app.font, size=12, fill=app.text_color, align='left')
    drawLabel('disable regular synthesizer functionality',  10, app.height-20,
              font=app.font, size=12, fill=app.text_color, align='left')

    for button in app.button_list_vocoder:
        draw_button(app, button)

def draw_how_to_play(app):
    draw_background(app)
    drawLabel('How To Play', app.width//2, 100, font=app.font, size=60, fill=app.text_color)
    drawLabel(f'{app.how_to_play_page + 1} / {app.how_to_play_page_count}', app.width//2, app.height - 100,
              font=app.font, size=30, fill=app.text_color)
    draw_button(app, app.button_exit)
    draw_button(app, app.button_left)
    draw_button(app, app.button_right)

    line_spacing = 20
    paragraph_start = app.height//4

    match app.how_to_play_page:
        case 0:
            paragraph = """\
To start, put your hands out so your camera can
see them fully, palms facing you. Position your
hands roughly 1-3 feet away from the camera, 
adjusting to fit your setup. Make sure that your
hands stand out from the background, and no light
source is directly hitting your camera."""
            for i in range(len(paragraph.splitlines())):
                line = paragraph.splitlines()[i]
                drawLabel(line, app.width//2, paragraph_start + line_spacing*i,
                          font=app.font, size=16, fill=app.text_color)
        case 1:
            paragraph = """\
Each of the numbered fingers corresponds to a note
in a 7 note scale. Both index fingers are an octave
apart from another. The lowest notes should be on
your left hand; if this is not the case, move
your hands away from the camera and try again."""
            for i in range(len(paragraph.splitlines())):
                line = paragraph.splitlines()[i]
                drawLabel(line, app.width // 2, paragraph_start + line_spacing * i,
                          font=app.font, size=16, fill=app.text_color)
        case 2:
            paragraph = """\
Bend your finger inward to play a note. The circle
on the tip of the finger should reach the base of
your finger. Once the circle is green, a note will
be played. All 8 notes can be played at the same
time, although this may cause lag."""
            for i in range(len(paragraph.splitlines())):
                line = paragraph.splitlines()[i]
                drawLabel(line, app.width // 2, paragraph_start + line_spacing * i,
                          font=app.font, size=16, fill=app.text_color)
        case 3:
            paragraph = """\
Thumbs control the octave that you play at. To
activate a thumb, move it towards the base of your
index finger. Thumb octaves operate in a binary
system: the right thumb increases the octave by 1
while the left thumb increases the octave by 2."""
            for i in range(len(paragraph.splitlines())):
                line = paragraph.splitlines()[i]
                drawLabel(line, app.width // 2, paragraph_start + line_spacing * i,
                          font=app.font, size=16, fill=app.text_color)
        case 4:
            paragraph = """\
Move your hand up to increase volume. Volume is
stereo, meaning that moving your left
hand up will increase audio on the left, and
moving your right will increase audio on the right."""
            for i in range(len(paragraph.splitlines())):
                line = paragraph.splitlines()[i]
                drawLabel(line, app.width // 2, paragraph_start + line_spacing * i,
                          font=app.font, size=16, fill=app.text_color)
        case 5:
            paragraph = """\
Finally, move your hands to the side to add
effects to your synth. Currently, only moving
your left hand will add a chorus effect to
your synth."""
            for i in range(len(paragraph.splitlines())):
                line = paragraph.splitlines()[i]
                drawLabel(line, app.width // 2, paragraph_start + line_spacing * i,
                          font=app.font, size=16, fill=app.text_color)
        case 6:
            paragraph = """\
Enjoy!"""
            for i in range(len(paragraph.splitlines())):
                line = paragraph.splitlines()[i]
                drawLabel(line, app.width // 2, paragraph_start + line_spacing * i,
                          font=app.font, size=16, fill=app.text_color)

def draw_button(app, button):
    if 'image_on' in button:
        image = button['image_on'] if button['hovered'] else button['image_off']
        drawImage(image, button['cx'], button['cy'], width=button['w'], height=button['h'])

    # Text buttons
    else:
        color = app.hovered_text_color if button['hovered'] else button['color']

        # Secret button stuff
        opacity = 100 if color is not None else 0
        if color is None: color = 'black'

        for i in range(len(button['text'].splitlines())):
            line = button['text'].splitlines()[i]
            drawLabel(line, button['cx'], button['cy'] + button['size']*1.5*i,
                      size=button['size'], font=app.font, fill=color, opacity=opacity, align='top-left')

def draw_background(app):
    x = (-1440 + app.width) / 2
    y = (-829 + app.height) / 2
    if app.screen == 'title_screen':
        drawImage('assets\\Background 1.1.png', x, y, width=1440, height=829, fill='pink')
    else:
        drawImage('assets\\Background.png', 0, 0, width=app.width, height=app.height, fill='pink')

def onMouseMove(app, mouse_x, mouse_y):
    match app.screen:
        case 'title_screen':     hoverButton(app, app.button_list_title_screen,     mouse_x, mouse_y)
        case 'menu_screen':      hoverButton(app, app.button_list_menu,             mouse_x, mouse_y)
        case 'chorus_effect':    hoverButton(app, app.button_list_chorus_effect,    mouse_x, mouse_y)
        case 'choose_key':       hoverButton(app, app.button_list_key,              mouse_x, mouse_y)
        case 'choose_scale':     hoverButton(app, app.button_list_scale,            mouse_x, mouse_y)
        case 'mono':             hoverButton(app, app.button_list_mono,             mouse_x, mouse_y)
        case 'choose_wave':      hoverButton(app, app.button_list_wave,             mouse_x, mouse_y)
        case 'edit_custom_wave': hoverButton(app, app.button_list_edit_custom_wave, mouse_x, mouse_y)
        case 'vocoder':          hoverButton(app, app.button_list_vocoder,          mouse_x, mouse_y)
        case 'how_to_play':      hoverButton(app, app.button_list_how_to_play,      mouse_x, mouse_y)

def hoverButton(app, button_list, mouse_x, mouse_y):
    for button in button_list:
        flag = mouse_in_button(app, button, mouse_x, mouse_y)
        if flag and not button['hovered'] and app.play_sound_cooldown == 0:  # make sure it is the first time hovering
            app.play_sound_cooldown = 10
            hover_sounds = ['assets\\Hover 1.wav', 'assets\\Hover 2.wav', 'assets\\Hover 3.wav', 'assets\\Hover 4.wav',
                            'assets\\Hover 5.wav']
            sfx = Sound(hover_sounds[randint(0, len(hover_sounds) - 1)])
            sfx.play()

        button['hovered'] = flag

def onMousePress(app, mouse_x, mouse_y):
    match app.screen:
        case 'title_screen':
            if   mouse_in_button(app, app.button_play, mouse_x, mouse_y):
                play_click_sound(app)
                if app.enable_vocoder:
                    cameraVocoder()
                else:
                    camera()
            elif mouse_in_button(app, app.button_menu, mouse_x, mouse_y):
                change_screen(app, 'menu_screen', app.button_menu)
            elif mouse_in_button(app, app.button_how_to_play, mouse_x, mouse_y):
                change_screen(app, 'how_to_play', app.button_how_to_play)

        case 'menu_screen':
            if   mouse_in_button(app, app.button_exit,              mouse_x, mouse_y):
                change_screen(app, 'title_screen',  app.button_exit)
            elif mouse_in_button(app, app.button_chorus,            mouse_x, mouse_y):
                change_screen(app, 'chorus_effect', app.button_chorus)
            elif mouse_in_button(app, app.button_choose_key,        mouse_x, mouse_y):
                change_screen(app, 'choose_key',    app.button_choose_key)
            elif mouse_in_button(app, app.button_choose_scale,      mouse_x, mouse_y):
                change_screen(app, 'choose_scale',  app.button_choose_scale)
            elif mouse_in_button(app, app.button_mono,              mouse_x, mouse_y):
                change_screen(app, 'mono',          app.button_mono)
            elif mouse_in_button(app, app.button_vocoder,           mouse_x, mouse_y):
                change_screen(app, 'vocoder',       app.button_vocoder)
            elif mouse_in_button(app, app.button_choose_wave,       mouse_x, mouse_y):
                change_screen(app, 'choose_wave', app.button_choose_wave)
            elif mouse_in_button(app, app.button_reset_to_defaults, mouse_x, mouse_y):
                play_click_sound(app)
                app.button_reset_to_defaults['hovered'] = False
                reset_settings_to_default()
            elif mouse_in_button(app, app.button_secret_music,      mouse_x, mouse_y):
                play_secret_music(app)

        case 'chorus_effect':
            test_mouse_in_slider(app, app.chorus_sliders,   mouse_x, mouse_y)
            if   mouse_in_button(app, app.button_exit,      mouse_x, mouse_y):
                change_screen(app, 'menu_screen',  app.button_exit)
            elif mouse_in_button(app, app.button_test_wave, mouse_x, mouse_y):
                # UPDATE PLAY WAVE HERE
                play_click_sound(app)
                if app.button_test_wave['color'] == app.text_color:
                    app.button_test_wave['color'] = app.neon_green
                else:
                    app.button_test_wave['color'] = app.text_color

        case 'choose_key':
            if   mouse_in_button(app, app.button_exit,       mouse_x, mouse_y):
                change_screen(app, 'menu_screen',  app.button_exit)
            elif mouse_in_button(app, app.button_increase_1, mouse_x, mouse_y):
                change_key(app, +1)
            elif mouse_in_button(app, app.button_decrease_1, mouse_x, mouse_y):
                change_key(app, -1)

        case 'choose_scale':
            if   mouse_in_button(app, app.button_exit,       mouse_x, mouse_y):
                change_screen(app, 'menu_screen',  app.button_exit)
            elif mouse_in_button(app, app.button_increase_1, mouse_x, mouse_y):
                change_scale(app, +1)
            elif mouse_in_button(app, app.button_decrease_1, mouse_x, mouse_y):
                change_scale(app, -1)

        case 'mono':
            if   mouse_in_button(app, app.button_exit,              mouse_x, mouse_y):
                change_screen(app, 'menu_screen', app.button_exit)
            elif mouse_in_button(app, app.button_enable_mono_on,  mouse_x, mouse_y) and app.enable_mono:
                play_click_sound(app)
                app.enable_mono = False
                update_settings_file('enable_mono', False)
                app.button_list_mono.remove(app.button_enable_mono_on)
                app.button_list_mono.append(app.button_enable_mono_off)
            elif mouse_in_button(app, app.button_enable_mono_off, mouse_x, mouse_y) and not app.enable_mono:
                play_click_sound(app)
                app.enable_mono = True
                update_settings_file('enable_mono', True)
                app.button_list_mono.remove(app.button_enable_mono_off)
                app.button_list_mono.append(app.button_enable_mono_on)

        case 'choose_wave':
            if   mouse_in_button(app, app.button_exit,             mouse_x, mouse_y):
                change_screen(app, 'menu_screen',      app.button_exit)
            elif mouse_in_button(app, app.button_edit_custom_wave, mouse_x, mouse_y):
                change_screen(app, 'edit_custom_wave', app.button_edit_custom_wave)
            elif mouse_in_button(app, app.button_increase_1,       mouse_x, mouse_y):
                play_click_sound(app)
                change_wave_shape(+1)
            elif mouse_in_button(app, app.button_decrease_1,       mouse_x, mouse_y):
                play_click_sound(app)
                change_wave_shape(-1)

        case 'edit_custom_wave':
            if   mouse_in_button(app, app.button_exit,              mouse_x, mouse_y):
                change_screen(app, 'menu_screen', app.button_exit)
            elif mouse_in_button(app, app.button_decrease_2,        mouse_x, mouse_y):
                if app.edit_wave_grid_cols == 1: return
                play_click_sound(app)
                app.edit_wave_grid_cols -= 1
            elif mouse_in_button(app, app.button_increase_2,        mouse_x, mouse_y):
                if app.edit_wave_grid_cols == 16: return
                play_click_sound(app)
                app.edit_wave_grid_cols += 1
            elif mouse_in_button(app, app.button_decrease_3,        mouse_x, mouse_y):
                if app.edit_wave_grid_rows == 1: return
                play_click_sound(app)
                app.edit_wave_grid_rows -= 1
            elif mouse_in_button(app, app.button_increase_3,        mouse_x, mouse_y):
                if app.edit_wave_grid_rows == 8: return
                play_click_sound(app)
                app.edit_wave_grid_rows += 1
            elif mouse_in_button(app, app.button_reset_custom_wave, mouse_x, mouse_y):
                play_click_sound(app)
                app.button_reset_custom_wave['hovered'] = False
                app.custom_wave = CreateWaveShape('sine', 44100).array
                update_settings_file('custom_wave', app.custom_wave.tolist())
            else:
                x0, y0 = edit_wave_check_in_point(app, mouse_x, mouse_y)
                if x0 is not None: app.edit_wave_curr_line = [x0, y0, mouse_x, mouse_y]

        case 'vocoder':
            if   mouse_in_button(app, app.button_exit,               mouse_x, mouse_y):
                change_screen(app, 'menu_screen',  app.button_exit)
            elif mouse_in_button(app, app.button_test_vocoder,       mouse_x, mouse_y):
                # UPDATE PLAY WAVE HERE
                play_click_sound(app)
                neon_green = rgb(57, 255, 20)
                if app.button_test_vocoder['color'] == app.text_color:
                    app.button_test_vocoder['color'] = app.neon_green
                else:
                    app.button_test_vocoder['color'] = app.text_color
            elif mouse_in_button(app, app.button_enable_vocoder_on,  mouse_x, mouse_y) and app.enable_vocoder:
                play_click_sound(app)
                app.enable_vocoder = False
                update_settings_file('enable_vocoder', False)
                app.button_list_vocoder.remove(app.button_enable_vocoder_on)
                app.button_list_vocoder.append(app.button_enable_vocoder_off)
            elif mouse_in_button(app, app.button_enable_vocoder_off, mouse_x, mouse_y) and not app.enable_vocoder:
                play_click_sound(app)
                app.enable_vocoder = True
                update_settings_file('enable_vocoder', True)
                app.button_list_vocoder.remove(app.button_enable_vocoder_off)
                app.button_list_vocoder.append(app.button_enable_vocoder_on)

        case 'how_to_play':
            if   mouse_in_button(app, app.button_exit, mouse_x, mouse_y):
                change_screen(app, 'title_screen', app.button_exit)
            elif mouse_in_button(app, app.button_left,  mouse_x, mouse_y):
                app.button_left['hovered'] = False
                play_click_sound(app)
                app.how_to_play_page = (app.how_to_play_page - 1) % app.how_to_play_page_count
            elif mouse_in_button(app, app.button_right, mouse_x, mouse_y):
                app.button_left['hovered'] = False
                play_click_sound(app)
                app.how_to_play_page = (app.how_to_play_page + 1) % app.how_to_play_page_count

def mouse_in_button(app, button, mouse_x, mouse_y):
    x_range = range(button['cx'], button['cx'] + button['w'])
    y_range = range(button['cy'], button['cy'] + button['h'])
    return mouse_x in x_range and mouse_y in y_range

def test_mouse_in_slider(app, slider_list, mouse_x, mouse_y):
    for slider in slider_list:
        if (mouse_x in range(slider.x_value - app.slider_size//2, slider.x_value + app.slider_size//2) and
            mouse_y in range(slider.y_value - app.slider_size//2, slider.y_value + app.slider_size//2)):
            slider.clicked_on = True
            break

def change_screen(app, screen, last_button):
    play_click_sound(app)
    last_button['hovered'] = False
    app.screen = screen

def play_click_sound(app):
    app.play_sound_cooldown = 10
    sfx = Sound('assets\\Click 1.wav')
    sfx.play()

def change_key(app, change):
    play_click_sound(app)
    settings = load_settings()
    current_key = settings['key']

    new_key_index = (get_key_index(current_key) + change) % 12
    new_key = get_key(new_key_index)
    update_settings_file('key', new_key)

def change_scale(app, change):
    play_click_sound(app)
    settings = load_settings()
    current_scale = settings['scale']

    new_scale_index = (get_scale_index(current_scale) + change) % 9
    new_scale = get_scale_from_index(new_scale_index)
    update_settings_file('scale', new_scale)

def edit_wave_check_in_point(app, mouse_x, mouse_y):
    # Grid variables
    grid_width = app.edit_wave_grid_width
    grid_height = app.edit_wave_grid_height
    grid_left = app.edit_wave_grid_left
    grid_top = app.edit_wave_grid_top

    # Cell size
    cell_width, cell_height, circle_size = get_cell_size(app)

    for row in range(app.edit_wave_grid_rows + 1):
        for col in range(app.edit_wave_grid_cols + 1):
            if distance(mouse_x, mouse_y, col*cell_width + grid_left, row*cell_height + grid_top) <= circle_size:
                return col*cell_width + grid_left, row*cell_height + grid_top

    return None, None

def play_secret_music(app):
    app.button_secret_music['color'] = 'green' if app.button_secret_music['color'] is None else None
    if app.button_secret_music['color'] == 'green':
        app.bg_music.play(restart=False, loop=True)
    else:
        app.bg_music.pause()

def onMouseDrag(app, mouse_x, mouse_y):
    match app.screen:
        case 'chorus_effect':
            for slider in app.chorus_sliders:
                if slider.clicked_on: slider.update_y_value(mouse_y)
        case 'edit_custom_wave':
            if app.edit_wave_curr_line == []: return
            app.edit_wave_curr_line = app.edit_wave_curr_line[:2] + [mouse_x, mouse_y]

def onMouseRelease(app, mouse_x, mouse_y):
    match app.screen:
        case 'chorus_effect':
            for slider in app.chorus_sliders:
                slider.clicked_on = False

        case 'edit_custom_wave':
            cell_width, cell_height, circle_size = get_cell_size(app)
            grid_x1, grid_y1 = edit_wave_check_in_point(app, mouse_x, mouse_y)

            if (app.edit_wave_curr_line != [] and grid_x1 is not None and
                distance(app.edit_wave_curr_line[0], app.edit_wave_curr_line[1], mouse_x, mouse_y) > circle_size):
                # This section was partially helped by AI (mainly to learn how to use numpy)
                x0, x1 = ((app.edit_wave_curr_line[0] - app.edit_wave_grid_left) / app.edit_wave_grid_width,
                          (grid_x1 - app.edit_wave_grid_left) / app.edit_wave_grid_width)
                y0, y1 = ((app.edit_wave_curr_line[1] - app.edit_wave_grid_top)  / app.edit_wave_grid_height,
                          (grid_y1 - app.edit_wave_grid_top)  / app.edit_wave_grid_height)

                # Normalize and prep values
                sample_rate = len(app.custom_wave)
                if x0 > x1:
                    (x0, y0), (x1, y1) = (x1, y1), (x0, y0)
                x0, x1 = int(x0*sample_rate), int(x1*sample_rate)
                x0 = max(0, min(x0, sample_rate - 1))  # clamp x0
                x1 = max(0, min(x1, sample_rate - 1))  # clamp x1

                y0, y1 = 1 - 2*y0, 1 - 2*y1  # normalize y values to fit to (-1, 1)

                # Add line to array
                num_samples = (x1 - x0 + 1)
                line = np.linspace(y0, y1, num_samples)
                app.custom_wave[x0:x1+1] = line  # replace the custom wave with the line

                update_settings_file('custom_wave', app.custom_wave.tolist())

            app.edit_wave_curr_line = []

def onStep(app):
    load_buttons(app)
    update_edit_wave_grid(app)
    if app.play_sound_cooldown != 0: app.play_sound_cooldown -= 1

    update_slider_flag = True
    for slider in app.chorus_sliders:
        if slider.clicked_on: update_slider_flag = False
    if update_slider_flag: load_buttons(app)

def main():
    runApp()

if __name__ == '__main__':
    main()