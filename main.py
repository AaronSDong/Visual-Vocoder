from cmu_graphics import *
from cmu_graphics.cmu_graphics import App
from camera import camera

def onAppStart(app):
    app.width = 800
    app.height = 800
    app.button_menu = {
        'cx': 275,
        'cy': 550,
        'w': 250,
        'h': 125,
        'hovered': False,
        'image_off': 'Menu Button.png',
        'image_on': 'Menu Button On.png',
    }
    app.button_play = {
        'cx': 275,
        'cy': 350,
        'w': 250,
        'h': 125,
        'hovered': False,
        'image_off': 'Play Button.png',
        'image_on': 'Play Button On.png',
    }
    app.button_list = [app.button_menu, app.button_play]
    app.bg_music = Sound('bgMusic.mp3')
    #app.bg_music.play(restart=True, loop=True)

def redrawAll(app):
    draw_button(app, app.button_menu)
    draw_button(app, app.button_play)
    drawLabel('Visual Synthesizer!', 400, 200, font='cosmic sans', size=60)

def draw_button(app, button):
    if button['hovered']:
        drawImage(button['image_on'], button['cx'], button['cy'], width=button['w'], height=button['h'])
    else:
        drawImage(button['image_off'], button['cx'], button['cy'], width=button['w'], height=button['h'])

def onMouseMove(app, mouse_x, mouse_y):
    for button in app.button_list:
        button['hovered'] = mouse_in_button(app, button, mouse_x, mouse_y)

def onMousePress(app, mouse_x, mouse_y):
    if mouse_in_button(app, app.button_play, mouse_x, mouse_y):
        camera()

def mouse_in_button(app, button, mouse_x, mouse_y):
    x_range = range(button['cx'], button['cx'] + button['w'])
    y_range = range(button['cy'], button['cy'] + button['h'])
    return mouse_x in x_range and mouse_y in y_range

def main():
    runApp()

if __name__ == '__main__':
    main()