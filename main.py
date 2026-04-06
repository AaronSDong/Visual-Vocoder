from cmu_graphics import *
from cmu_graphics.cmu_graphics import App
from camera import camera


def onAppStart(app):
    app.width = 800
    app.height = 800
    app.buttonMenu = {
        'cx': 275,
        'cy': 550,
        'w': 250,
        'h': 125,
        'hovered': False,
        'imageOff': 'Menu Button.png',
        'imageOn': 'Menu Button On.png',
    }
    app.buttonPlay = {
        'cx': 275,
        'cy': 350,
        'w': 250,
        'h': 125,
        'hovered': False,
        'imageOff': 'Play Button.png',
        'imageOn': 'Play Button On.png',
    }
    app.buttonList = [app.buttonMenu, app.buttonPlay]
    app.bgMusic = Sound('bgMusic.mp3')
    #app.bgMusic.play(restart=True, loop=True)

def redrawAll(app):
    drawButton(app, app.buttonMenu)
    drawButton(app, app.buttonPlay)
    drawLabel('Visual Synthesizer!', 400, 200, font='cosmic sans', size=60)

def drawButton(app, button):
    if button['hovered']:
        drawImage(button['imageOn'], button['cx'], button['cy'], width=button['w'], height=button['h'])
    else:
        drawImage(button['imageOff'], button['cx'], button['cy'], width=button['w'], height=button['h'])

def onMouseMove(app, mouseX, mouseY):
    for button in app.buttonList:
        button['hovered'] = mouseInButton(app, button, mouseX, mouseY)

def onMousePress(app, mouseX, mouseY):
    if mouseInButton(app, app.buttonPlay, mouseX, mouseY):
        camera()

def mouseInButton(app, button, mouseX, mouseY):
    xRange = range(button['cx'], button['cx'] + button['w'])
    yRange = range(button['cy'], button['cy'] + button['h'])
    return mouseX in xRange and mouseY in yRange

def main():
    runApp()

if __name__ == '__main__':
    main()