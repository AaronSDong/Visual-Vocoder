from cmu_graphics import *
from cmu_graphics.cmu_graphics import App


def onAppStart(app):
    app.width = 800
    app.height = 800
    app.buttonMenu = {
        'cx': 200,
        'cy': 400,
        'w': 400,
        'h': 200,
        'hovered': False,
        'imageOff': 'Menu Button.png',
        'imageOn': 'Menu Button On.png',
    }
    app.buttonList = [app.buttonMenu]
    app.bgMusic = Sound('bgMusic.mp3')
    app.bgMusic.play(restart=True, loop=True)

def redrawAll(app):
    drawMenuButton(app, app.buttonMenu)
    drawLabel('Visual Synthesizer!', 400, 200, font='arial', size=60)

def drawMenuButton(app, button):
    if app.buttonMenu['hovered']:
        drawImage(button['imageOn'], button['cx'], button['cy'], width=button['w'], height=button['h'])
    else:
        drawImage(button['imageOff'], button['cx'], button['cy'], width=button['w'], height=button['h'])

def onMouseMove(app, mouseX, mouseY):
    for button in app.buttonList:
        button['hovered'] = checkButtonHovered(app, app.buttonMenu, mouseX, mouseY)

def checkButtonHovered(app, button, mouseX, mouseY):
    xRange = range(button['cx'], button['cx'] + button['w'])
    yRange = range(button['cy'], button['cy'] + button['h'])
    return mouseX in xRange and mouseY in yRange

def main():
    runApp()

if __name__ == '__main__':
    main()