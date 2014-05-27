FallingSpeed=3
WindowHeight=800
WindowWidth=1024



#import everything

import time, random, math
import os, pygame
from pygame.locals import *



        
#quick function to load an image
def load_image(name):

    return pygame.image.load(name).convert()




#here's the full code
def main(score,total):
    White=255
    result=""
    flag=0

    pygame.init()
    pygame.display.init 
    pygame.mixer.init()
    sound= pygame.mixer.Sound("resources/result.wav")
    
    screen = pygame.display.set_mode((WindowWidth, WindowHeight))
    #up = load_image('up.gif')
    #down = load_image('down.gif')
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))
    
    
    ## start timer###################################
    start = time.time()
    print start

    myfont = pygame.font.SysFont("monospace", 40)

    if(int(score)>total/2):
        result="A"
    elif(int(score)>total/5):
        result="B"
    elif(int(score)>0):
        result="C"
    else:
        result="D"
        
   

    while True:
        pygame.time.wait(5)
        screen.blit(background, (0,0))# clearAll
        elapsed = (time.time() - start)

        if(elapsed>1 and White>0): # dim effect
            White-=1

        label = myfont.render(str(score), 1, (White,White,0))
        screen.blit(label, (35, WindowHeight-100))


        ##draw lines##
        pygame.draw.lines(screen, (White,White,White) , False, [(200+26,0),(200+26,WindowHeight)], 3)
        pygame.draw.lines(screen, (White,White,White) , False, [(400+26,0),(400+26,WindowHeight)], 3)
        pygame.draw.lines(screen, (White,White,White) , False, [(600+26,0),(600+26,WindowHeight)], 3)
        pygame.draw.lines(screen, (White,White,White) , False, [(800+26,0),(800+26,WindowHeight)], 3)
        pygame.draw.lines(screen, (White,White,White) , False, [(0,WindowHeight-100),(WindowWidth,WindowHeight-100)], 3)
        pygame.draw.lines(screen, (White,White,White) , False, [(0,WindowHeight-200),(WindowWidth,WindowHeight-200)], 3)


        if(elapsed>3):
            myfont = pygame.font.SysFont("monospace", 80)
            labelScore=myfont.render("Score: ", 1, (255,255,0))
            screen.blit(labelScore, (WindowWidth/2-240, 300))
            labelResult=myfont.render("Result: ", 1, (255,255,0))
            screen.blit(labelResult, (WindowWidth/2-240, 400))
            if(flag==0):
                sound.play()
                flag=1
            

        if(elapsed>4):#Score
            myfont = pygame.font.SysFont("monospace", 80)
            labelScore=myfont.render(str(score), 1, (255,255,0))
            screen.blit(labelScore, (WindowWidth/2+80, 300))
            if flag==1:
                sound.play()
                flag=2

        if(elapsed>5):#Result
            myfont = pygame.font.SysFont("monospace", 80)
            labelResult=myfont.render(result, 1, (255,255,0))
            screen.blit(labelResult, (WindowWidth/2+120, 400))
            if flag==2:
                sound.play()
                flag=3

        if(elapsed>9):
            return

        
        for event in pygame.event.get():
            if event.type ==QUIT:
                return 
        
        pygame.display.update()
        
if __name__ == '__main__': main(89,90)        


