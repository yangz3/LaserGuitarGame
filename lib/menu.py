
import pygame, sys

def menu(screen, menu, x_pos = 100, y_pos = 100, font = None,
        size = 70, distance = 1.4, fgcolor = (255,255,255),
        cursorcolor = (255,0,0), exitAllowed = True):
    # Draw the Menupoints
    pygame.font.init()
    if font == None:
        myfont = pygame.font.Font(None, size)
    else:
        myfont = pygame.font.SysFont(font, size)
    cursorpos = 0
    renderWithChars = False
    for i in menu:
        if renderWithChars == False:
            text =  myfont.render(i,True, fgcolor)
        else:
            text =  myfont.render(i,True, fgcolor)
        textrect = text.get_rect()
        textrect = textrect.move(x_pos, 
                   (size // distance * cursorpos) + y_pos)
        screen.blit(text, textrect)
        pygame.display.update(textrect)
        cursorpos += 1
        if cursorpos == 9:
            renderWithChars = True
            char = 65

    # Draw the ">", the Cursor
    cursorpos = 0
    cursor = myfont.render(">", True, cursorcolor)
    cursorrect = cursor.get_rect()
    cursorrect = cursorrect.move(x_pos - (size // distance),
                 (size // distance * cursorpos) + y_pos)

    # The whole While-loop takes care to show the Cursor, move the
    # Cursor and getting the Keys (1-9 and A-Z) to work...
    ArrowPressed = True
    exitMenu = False
    clock = pygame.time.Clock()
    filler = pygame.Surface.copy(screen)
    fillerrect = filler.get_rect()
    while True:
        clock.tick(30)
        if ArrowPressed == True:
            screen.blit(filler, fillerrect)
            pygame.display.update(cursorrect)
            cursorrect = cursor.get_rect()
            cursorrect = cursorrect.move(x_pos - (size // distance),
                         (size // distance * cursorpos) + y_pos)
            pygame.display.update()
            screen.blit(cursor, cursorrect)
            pygame.display.update(cursorrect)
            ArrowPressed = False
        if exitMenu == True:
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cursorpos = -1
                exitMenu = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and exitAllowed == True:
                    if cursorpos == len(menu) - 1:
                        exitMenu = True
                    else:
                        cursorpos = len(menu) - 1; ArrowPressed = True

                if event.key == pygame.K_UP:
                    ArrowPressed = True
                    if cursorpos == 0:
                        cursorpos = len(menu) - 1
                    else:
                        cursorpos -= 1
                elif event.key == pygame.K_DOWN:
                    ArrowPressed = True
                    if cursorpos == len(menu) - 1:
                        cursorpos = 0
                    else:
                        cursorpos += 1
                elif event.key == pygame.K_KP_ENTER or \
                     event.key == pygame.K_RETURN:
                            exitMenu = True
    return cursorpos
if __name__ == '__main__':
    sys.exit()
