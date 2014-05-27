import pygame, pygame.font, pygame.event, pygame.draw, string
from pygame.locals import *

def getkey():
    while 1:
        event = pygame.event.poll()
        if event.type == KEYDOWN:
            return (event.key, event.unicode)
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
def displaybox(screen, message):
    #Print a message in a box in the middle of the screen
    fontobject = pygame.font.Font(None,18)
    pygame.draw.rect(screen, (0,0,0),
        ((screen.get_width() / 2) - 150,
        (screen.get_height() / 2) - 10,
        200,20), 0)
    
    pygame.draw.rect(screen, (255,255,255),
        ((screen.get_width() / 2) - 152,
        (screen.get_height() / 2) - 12,
        204,24), 1)
    if len(message) != 0:
        screen.blit(fontobject.render(message, 1, (255,255,255)),
        ((screen.get_width() / 2) - 150, (screen.get_height() / 2) - 10))
    pygame.display.flip()

def ask(screen, question):
  
    pygame.font.init()
    currentString = []
    displaybox(screen, question + ": " + "".join(currentString))
    while 1:
        (inkey, unich) = getkey()
        if inkey == K_BACKSPACE:
            currentString = currentString[0:-1]
        elif inkey == K_RETURN:
            break
        elif inkey == K_MINUS:
            currentString.append("_")
        elif inkey == K_ESCAPE:
            break
        elif inkey <= 127:
            currentString.append(unich)
        displaybox(screen, question + ": " + "".join(currentString))
    return "".join(currentString)

if __name__ == '__main__': pass
