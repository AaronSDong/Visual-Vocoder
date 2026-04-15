from cmu_graphics import *
from camera import camera

def onAppStart(app):
    app.width = 800
    app.height = 800

    app.screen = 'title_screen'
    app.how_to_play_page = 0
    app.how_to_play_page_count = 7
    load_buttons(app)

    app.bg_music = Sound('bgMusic.mp3')
    #app.bg_music.play(restart=True, loop=True)
    app.font = 'Pixelated Elegance'

def load_buttons(app):
    if not hasattr(app, 'button_play'): app.button_play = {}  # idea taken from AI
    app.button_play['cx'] = app.width//2 - 100
    app.button_play['cy'] = int(app.height * .4375)
    app.button_play['w'] = 200
    app.button_play['h'] = 100
    app.button_play['image_off'] = 'Play Button.png'
    app.button_play['image_on'] = 'Play Button On.png'
    app.button_play['hovered'] = app.button_play.get('hovered', False)

    if not hasattr(app, 'button_menu'): app.button_menu = {}
    app.button_menu['cx'] = app.width // 2 - 100
    app.button_menu['cy'] = int(app.height * .625)
    app.button_menu['w'] = 200
    app.button_menu['h'] = 100
    app.button_menu['image_off'] = 'Menu Button.png'
    app.button_menu['image_on'] = 'Menu Button On.png'
    app.button_menu['hovered'] = app.button_menu.get('hovered', False)

    if not hasattr(app, 'button_how_to_play'): app.button_how_to_play = {}
    app.button_how_to_play['cx'] = app.width // 2 - 100
    app.button_how_to_play['cy'] = int(app.height * .8125)
    app.button_how_to_play['w'] = 200
    app.button_how_to_play['h'] = 100
    app.button_how_to_play['image_off'] = 'How To Play Button.png'
    app.button_how_to_play['image_on'] = 'How To Play Button On.png'
    app.button_how_to_play['hovered'] = app.button_how_to_play.get('hovered', False)

    if not hasattr(app, 'button_exit'): app.button_exit = {}
    app.button_exit['cx'] = app.width - 90
    app.button_exit['cy'] = 30
    app.button_exit['w'] = 50
    app.button_exit['h'] = 50
    app.button_exit['image_off'] = 'How To Play Button.png'
    app.button_exit['image_on'] = 'How To Play Button On.png'
    app.button_exit['hovered'] = app.button_exit.get('hovered', False)

    if not hasattr(app, 'button_left'): app.button_left = {}
    app.button_left['cx'] = app.width // 2 - 70
    app.button_left['cy'] = app.height - 75
    app.button_left['w'] = 50
    app.button_left['h'] = 50
    app.button_left['image_off'] = 'How To Play Button.png'
    app.button_left['image_on'] = 'How To Play Button On.png'
    app.button_left['hovered'] = app.button_left.get('hovered', False)

    if not hasattr(app, 'button_right'): app.button_right = {}
    app.button_right['cx'] = app.width // 2 + 20
    app.button_right['cy'] = app.height - 75
    app.button_right['w'] = 50
    app.button_right['h'] = 50
    app.button_right['image_off'] = 'How To Play Button On.png'
    app.button_right['image_on'] = 'How To Play Button.png'
    app.button_right['hovered'] = app.button_right.get('hovered', False)

    if not hasattr(app, 'button_chorus'): app.button_chorus = {}
    app.button_chorus['cx'] = app.width // 8
    app.button_chorus['cy'] = app.height // 4
    app.button_chorus['w'] = 140
    app.button_chorus['h'] = 70
    app.button_chorus['text'] = 'Chorus\nEffect'
    app.button_chorus['size'] = 30
    app.button_chorus['color'] = 'purple'
    app.button_chorus['hovered'] = app.button_chorus.get('hovered', False)

    if not hasattr(app, 'button_test_wave'): app.button_test_wave = {}
    app.button_test_wave['cx'] = app.width // 2 - (210//2)
    app.button_test_wave['cy'] = 3*app.height // 4
    app.button_test_wave['w'] = 210
    app.button_test_wave['h'] = 25
    app.button_test_wave['text'] = 'Test Wave'
    app.button_test_wave['size'] = 30
    app.button_test_wave['color'] = app.button_test_wave.get('color', 'red')
    app.button_test_wave['hovered'] = app.button_test_wave.get('hovered', False)

    app.button_list_title_screen = [app.button_play, app.button_menu, app.button_how_to_play]
    app.button_list_menu = [app.button_exit, app.button_chorus]
    app.button_list_chorus_effect = [app.button_exit, app.button_test_wave]
    app.button_list_how_to_play = [app.button_exit, app.button_right, app.button_left]

def redrawAll(app):
    match app.screen:
        case 'title_screen':  draw_title_screen(app)
        case 'menu_screen':   draw_menu_screen(app)
        case 'chorus_effect': draw_chorus_effect(app)
        case 'how_to_play':   draw_how_to_play(app)

def draw_title_screen(app):
    draw_background(app)
    drawLabel('Visual Synthesizer!', app.width // 2, app.height // 4, font=app.font, size=40)
    for button in app.button_list_title_screen:
        draw_button(app, button)

def draw_menu_screen(app):
    draw_background(app)
    drawLabel('Menu', app.width//2, 100, font=app.font, size=60)
    for button in app.button_list_menu:
        draw_button(app, button)

def draw_chorus_effect(app):
    draw_background(app)
    drawLabel('Chorus Effect', app.width//2, 100, font=app.font, size=60)
    drawImage('Menu Button.png', app.width//2, int(app.height * .45), width=600, height=300, align='center')
    for button in app.button_list_chorus_effect:
        draw_button(app, button)

    slider_x0, slider_x1, slider_x2, slider_x3 = .4*app.width, .52*app.width, .64*app.width, .76*app.width
    slider_y0, slider_y1, slider_y2, slider_y3 = app.height // 2, app.height // 2, app.height // 2, app.height // 2,
    slider_list = [(slider_x0, slider_y0), (slider_x1, slider_y1), (slider_x2, slider_y2), (slider_x3, slider_y3)]
    for slider in slider_list:
        drawRect(slider[0], slider[1], 50, 20, align='center', fill='white')

def draw_how_to_play(app):
    draw_background(app)
    drawLabel('How To Play', app.width//2, 100, font=app.font, size=60)
    drawLabel(f'{app.how_to_play_page + 1} / {app.how_to_play_page_count}', app.width//2, app.height - 100,
              font=app.font, size=30)
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
                drawLabel(line, app.width//2, paragraph_start + line_spacing*i, font=app.font, size=16)
        case 1:
            paragraph = """\
Each of the numbered fingers corresponds to a note
in a 7 note scale. Both index fingers are an octave
apart from another. The lowest notes should be on
your left hand; if this is not the case, move
your hands away from the camera and try again."""
            for i in range(len(paragraph.splitlines())):
                line = paragraph.splitlines()[i]
                drawLabel(line, app.width // 2, paragraph_start + line_spacing * i, font=app.font, size=16)
        case 2:
            paragraph = """\
Bend your finger inward to play a note. The circle
on the tip of the finger should reach the base of
your finger. Once the circle is green, a note will
be played. All 8 notes can be played at the same
time, although this may cause lag."""
            for i in range(len(paragraph.splitlines())):
                line = paragraph.splitlines()[i]
                drawLabel(line, app.width // 2, paragraph_start + line_spacing * i, font=app.font, size=16)
        case 3:
            paragraph = """\
Thumbs control the octave that you play at. To
activate a thumb, move it towards the base of your
index finger. Thumb octaves operate in a binary
system: the right thumb increases the octave by 1
while the left thumb increases the octave by 2."""
            for i in range(len(paragraph.splitlines())):
                line = paragraph.splitlines()[i]
                drawLabel(line, app.width // 2, paragraph_start + line_spacing * i, font=app.font, size=16)
        case 4:
            paragraph = """\
Move your hand up to increase volume. Volume is
stereo, meaning that moving your left
hand up will increase audio on the left, and
moving your right will increase audio on the right."""
            for i in range(len(paragraph.splitlines())):
                line = paragraph.splitlines()[i]
                drawLabel(line, app.width // 2, paragraph_start + line_spacing * i, font=app.font, size=16)
        case 5:
            paragraph = """\
Finally, move your hands to the side to add
effects to your synth. Currently, only moving
your left hand will add a chorus effect to
your synth."""
            for i in range(len(paragraph.splitlines())):
                line = paragraph.splitlines()[i]
                drawLabel(line, app.width // 2, paragraph_start + line_spacing * i, font=app.font, size=16)
        case 6:
            paragraph = """\
Enjoy!"""
            for i in range(len(paragraph.splitlines())):
                line = paragraph.splitlines()[i]
                drawLabel(line, app.width // 2, paragraph_start + line_spacing * i, font=app.font, size=16)

def draw_button(app, button):
    if 'image_on' in button:
        image = button['image_on'] if button['hovered'] else button['image_off']
        drawImage(image, button['cx'], button['cy'], width=button['w'], height=button['h'])

    else:
        color = 'cyan' if button['hovered'] else button['color']
        for i in range(len(button['text'].splitlines())):
            line = button['text'].splitlines()[i]
            drawLabel(line, button['cx'], button['cy'] + button['size']*1.5*i,
                      size=button['size'], font=app.font, fill=color, align='top-left')

def draw_background(app):
    drawRect(0, 0, app.width, app.height, fill='pink')

def onMouseMove(app, mouse_x, mouse_y):
    match app.screen:
        case 'title_screen':  hoverButton(app, app.button_list_title_screen,  mouse_x, mouse_y)
        case 'menu_screen':   hoverButton(app, app.button_list_menu,          mouse_x, mouse_y)
        case 'chorus_effect': hoverButton(app, app.button_list_chorus_effect, mouse_x, mouse_y)
        case 'how_to_play':   hoverButton(app, app.button_list_how_to_play,   mouse_x, mouse_y)

def hoverButton(app, button_list, mouse_x, mouse_y):
    for button in button_list:
        button['hovered'] = mouse_in_button(app, button, mouse_x, mouse_y)

def onMousePress(app, mouse_x, mouse_y):
    match app.screen:
        case 'title_screen':
            if   mouse_in_button(app, app.button_play, mouse_x, mouse_y): camera()
            elif mouse_in_button(app, app.button_menu, mouse_x, mouse_y):
                change_screen(app, 'menu_screen', app.button_menu)
            elif mouse_in_button(app, app.button_how_to_play, mouse_x, mouse_y):
                change_screen(app, 'how_to_play', app.button_how_to_play)

        case 'menu_screen':
            if   mouse_in_button(app, app.button_exit,   mouse_x, mouse_y):
                change_screen(app, 'title_screen',  app.button_exit)
            elif mouse_in_button(app, app.button_chorus, mouse_x, mouse_y):
                change_screen(app, 'chorus_effect', app.button_chorus)

        case 'chorus_effect':
            if   mouse_in_button(app, app.button_exit,      mouse_x, mouse_y):
                change_screen(app, 'menu_screen',  app.button_exit)
            elif mouse_in_button(app, app.button_test_wave, mouse_x, mouse_y):
                # play wave

                neon_green = rgb(57, 255, 20)
                app.button_test_wave['color'] = 'red' if app.button_test_wave['color'] == neon_green else neon_green

        case 'how_to_play':
            if   mouse_in_button(app, app.button_exit, mouse_x, mouse_y):
                change_screen(app, 'title_screen', app.button_exit)
            elif mouse_in_button(app, app.button_left,  mouse_x, mouse_y):
                app.button_left['hovered'] = False
                app.how_to_play_page = (app.how_to_play_page - 1) % app.how_to_play_page_count
            elif mouse_in_button(app, app.button_right, mouse_x, mouse_y):
                app.button_left['hovered'] = False
                app.how_to_play_page = (app.how_to_play_page + 1) % app.how_to_play_page_count


def mouse_in_button(app, button, mouse_x, mouse_y):
    x_range = range(button['cx'], button['cx'] + button['w'])
    y_range = range(button['cy'], button['cy'] + button['h'])
    return mouse_x in x_range and mouse_y in y_range

def change_screen(app, screen, last_button):
    last_button['hovered'] = False
    app.screen = screen

def onStep(app):
    load_buttons(app)

def main():
    runApp()

if __name__ == '__main__':
    main()