FallingSpeed=3
WindowHeight=800
WindowWidth=1024
NUMSTARS=5
MaxNumOfExplosions=5
MaxNumOfArrows=5
MaxNumOfCircles=5



#import everything
import threading
import ctypes
import time, random, math, serial
import os, sys, pygame
from pygame.locals import *
import gameover


port = 'COM7'
baud = 9600
serial_port = serial.Serial(port, baud, timeout=0)



class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self):
        super(StoppableThread, self).__init__(target=read_from_port, args=(serial_port,))
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()



def read_from_port(ser):# read from all data in wait and extract the last line
    global last_received
    buffer=""
    while True:
        time.sleep(0.001)# must have this sleep or the cpu overloaded the interface really slow
        # the delay of this should be less than the delay in arduino
        if(isQuit!=True):
            buffer = buffer + ser.read(ser.inWaiting())
            lines = buffer.split('$') 
            if(len(lines)>=2):# Guaranteed to have at least 2 entries
                last_received = lines[-2]
                buffer=lines[-1]
                #print last_received
            else: pass
        else:
            serial_port.close()
            return


    
        

class HitStringAnimation(object):
    def __init__(self, NumString, Direction):
        self.numString=NumString
        self.direction=Direction
        self.rad=5
        self.state=0
    def init(self, NumString, Direction):
        self.numString=NumString
        self.direction=Direction
        self.rad=5
        self.state=1

    def expand(self):
        self.rad+=3
        if self.rad>40:
            self.state=0
            
    def draw(self, surface, lev):
        if lev==3:
            if self.direction==1:
                pygame.draw.circle(surface, (0,255,0),((self.numString%5)*200+26,WindowHeight-100), self.rad, 2)
            else:
                pygame.draw.circle(surface, (255,0,0),((self.numString%5)*200+26,WindowHeight-100), self.rad, 2)
        elif lev==2:
            pygame.draw.circle(surface, (220,20,60),((self.numString%5)*200+26,WindowHeight-100), self.rad, 2)
        else:
            pygame.draw.circle(surface, (255,160,0),((self.numString%5)*200+26,WindowHeight-100), self.rad, 2)
        


class Explosion:
    def init_star(self):
        dir = random.randrange(32)/10+1.7
        velmult = 20
        vel = [math.sin(dir) * velmult, math.cos(dir) * velmult]
        return vel, [self.cx,self.cy]

    def __init__(self, CX, CY, Color):
        self.cx=CX
        self.cy=CY
        self.stars=[]
        self.state=False
        self.color=Color
        for x in range(NUMSTARS):
            star = self.init_star()
            vel, pos = star
            self.stars.append(star)

    def init(self, CX, CY, Color):
        self.cx=CX
        self.cy=CY
        self.stars=[]
        self.state=False
        self.color=Color
        for x in range(NUMSTARS):
            star = self.init_star()
            vel, pos = star
            self.stars.append(star)
            
    def move(self):
        self.state=False
        for vel, pos in self.stars:
            pos[0] = pos[0] + vel[0]
            pos[1] = pos[1] + vel[1]
            if 0 <= pos[0] <=WindowWidth and 0 <= pos[1] <= WindowHeight:# there still exist some stars in the canvas
                self.state=True
            elif(vel[0]>2 and vel[1]>2):
                vel[0] = vel[0] * 0.95
                vel[1] = vel[1] * 0.95
                
    def draw_stars(self, surface, level):
        for vel, pos in self.stars:
            pos = (int(pos[0]), int(pos[1]))
            #surface.set_at(pos, color)
            if level==3:
                pygame.draw.polygon(surface, self.color, [(pos[0]-6,pos[1]+2),(pos[0],pos[1]-7),(pos[0]+7,pos[1]),(pos[0]+4,pos[1]+7)], 0)
            elif level==2:
                pygame.draw.polygon(surface, (220,20,60), [(pos[0]-6,pos[1]+2),(pos[0],pos[1]-7),(pos[0]+7,pos[1]),(pos[0]+4,pos[1]+7)], 0)
            else:
                pygame.draw.polygon(surface, (255,160,0), [(pos[0]-6,pos[1]+2),(pos[0],pos[1]-7),(pos[0]+7,pos[1]),(pos[0]+4,pos[1]+7)], 0)


#our game object class
class GameObject:
    def __init__(self, image, numString, Y, speed,Color,ID):
        self.speed = speed
        self.image = image
        self.numstring=numString
        self.pos = image.get_rect().move((numString%5)*200, Y)# the initial position of image
        self.color=Color
        self.state=0
        self.id=ID

    def init(self, image, numString, Y, speed,Color,ID):
        self.speed = speed
        self.image = image
        self.numstring=numString
        self.pos = image.get_rect().move((numString%5)*200, Y)# the initial position of image
        self.color=Color
        self.state=0
        self.id=ID
        
    def move(self):
        self.pos = self.pos.move(0,self.speed) # pos <0,0,53,68>
    
    def checkHit(self):# arrow is now in the ready area within which string must be trigered
        if abs(self.pos.bottom - WindowHeight+100)<=FallingSpeed/2:
            return True

    def checkHitBottom(self):
        if abs(self.pos.bottom - WindowHeight)<=FallingSpeed/2:
            return True
        
#quick function to load an image
def load_image(name):

    return pygame.image.load(name).convert()





#here's the full code
def main(filename,level,whichMusic):
    global isQuit
    isQuit=False
    ###### read the tempo.txt file to generate the orders of falling of arrows######
    arrowTime=[]
    numString=[]
    directions=[]
    pointer=0
    timeSet=set()


    
    with open("tempo.txt", "r") as f:
        lineNumber = 0
        for line in f:
            line = line.replace("\n","") # remove the trailing newline
            line = line.replace("\r","") # remove the trailing newline
            line= line.split(" ")

            arrowTime.append(float(line[0]))
            numString.append(int(line[1]))
            directions.append(int(line[2]))

    
    Score=0
    pygame.init()
    pygame.display.init 
    pygame.mixer.init()
    noise= pygame.mixer.Sound("resources/noise.wav")
    music= pygame.mixer.Sound(filename)
    screen = pygame.display.set_mode((WindowWidth, WindowHeight))
    if level==3:
        up = load_image('resources/up.gif')
        down = load_image('resources/down.gif')
        up2 = load_image('resources/up2.gif')
        down2 = load_image('resources/down2.gif')
    elif level==2:
        up = load_image('resources/bobo.gif')
        down = load_image('resources/bobo.gif')
        up2 = load_image('resources/bobo2.gif')
        down2 = load_image('resources/bobo2.gif')
    else:
        up = load_image('resources/bo.gif')
        down = load_image('resources/bo.gif')
        up2 = load_image('resources/bo2.gif')
        down2 = load_image('resources/bo2.gif')
        
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))
    
    ## generate falling pieces ########################
    objects = []
    for i in xrange(MaxNumOfArrows):
        o=GameObject(up, 200, 0, FallingSpeed, (0,255,0),"0")
        objects.append(o)
    
    ## start timer ###################################
    start = time.time()
    print start

    ## explosion ###################################
    explosions=[]
    for i in xrange(MaxNumOfExplosions):
        explosion=Explosion(0,0, (0,0,0))
        explosions.append(explosion)

     ## circles ###################################
    circles=[]
    for i in xrange(MaxNumOfCircles):
        cir=HitStringAnimation(1,1)
        circles.append(cir)

    myfont = pygame.font.SysFont("monospace", 40)
    myfont2 = pygame.font.SysFont("monospace", 30)
    myfont3 = pygame.font.SysFont("monospace", 15)



    ## thread ###################################
    #thread=StoppableThread(target=read_from_port, args=(serial_port,))

    t = threading.Thread(target=read_from_port, args=(serial_port,))
    #thread.daemon = True
    t.setDaemon(True)
    t.start()
    #t.join()

    music.play()# play music should be close to while true to make sure the delay is small


    while True:
        pygame.time.wait(5)
        screen.blit(background, (0,0))# clearAll
        label = myfont.render(str(Score), 1, (255,255,0))
        screen.blit(label, (30, WindowHeight-100))
        
        label2 = myfont2.render("Level: "+str(level), 1, (255,255,255))
        screen.blit(label2, (30, 30))
        
   
        label3 = myfont3.render(whichMusic.split(".")[0], 1, (255,255,255))
        screen.blit(label3, (30, 70))

  
        ##draw lines##
        pygame.draw.lines(screen, (255,255,255) , False, [(200+26,0),(200+26,WindowHeight)], 3)
        pygame.draw.lines(screen, (255,255,255) , False, [(400+26,0),(400+26,WindowHeight)], 3)
        pygame.draw.lines(screen, (255,255,255) , False, [(600+26,0),(600+26,WindowHeight)], 3)
        pygame.draw.lines(screen, (255,255,255) , False, [(800+26,0),(800+26,WindowHeight)], 3)
        pygame.draw.lines(screen, (255,255,255) , False, [(0,WindowHeight-100),(WindowWidth,WindowHeight-100)], 3)
        pygame.draw.lines(screen, (255,255,255) , False, [(0,WindowHeight-200),(WindowWidth,WindowHeight-200)], 3)

        
        for event in pygame.event.get():
            if event.type ==QUIT:
      
                isQuit=True
                music.stop()
                
                #pygame.quit()
                return True



        ##draw arrows##
        for o in objects:
            if (o.state==1):
                o.move()
                screen.blit(o.image, o.pos)
                if (o.checkHitBottom()):#one missed piece which hit the bottom of window
                    o.state=0
                    noise.play()
                    
                if(o.checkHit()):# hit the line and check if key is pressed
                    ## keyboard input to control circles####### NEED to combine with Serial DATA
                    serialData= last_received.split("\t")
                    print serialData

                    if level==1:
                        if (serialData[0]=="1") and (o.numstring==1) :
                            for c in circles:
                                if c.state==0:
                                    c.init(1,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break
                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break
                        if (serialData[1]=="1") and (o.numstring==2):
                            for c in circles:
                                if c.state==0:
                                    c.init(2,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break
                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break

                        if (serialData[2]=="1") and (o.numstring==3):
                            for c in circles:
                                if c.state==0:
                                    c.init(3,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break
                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break

                        if (serialData[3]=="1") and (o.numstring==4):
                            for c in circles:
                                if c.state==0:
                                    c.init(4,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break
                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break

                        if (o.numstring==6) and (serialData[0]=="1" and serialData[1]=="1"):
                    
                            for c in circles:
                                if c.state==0:
                                    c.init(1,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break
                                
                            for c in circles:
                                if c.state==0:
                                    c.init(2,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break  
                                
                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break

                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2+200,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break
                                
                        if (o.numstring==7) and (serialData[1]=="1" and serialData[2]=="1"):
                      
                            for c in circles:
                                if c.state==0:
                                    c.init(2,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break
                                
                            for c in circles:
                                if c.state==0:
                                    c.init(3,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break
                                
                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break

                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2+200,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break

                        if (o.numstring==8) and (serialData[2]=="1" and serialData[3]=="1"):
                           
                            for c in circles:
                                if c.state==0:
                                    c.init(3,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break

                            for c in circles:
                                if c.state==0:
                                    c.init(4,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break
                            
                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break

                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2+200,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break


                        
                    elif level==2:
                        
                        if (serialData[0]=="1") and (o.numstring==1) and ("1"==serialData[5]):
                            for c in circles:
                                if c.state==0:
                                    c.init(1,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break
                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break
                        if (serialData[1]=="1") and (o.numstring==2)and ("1"==serialData[5]):
                            for c in circles:
                                if c.state==0:
                                    c.init(2,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break
                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break

                        if (serialData[2]=="1") and (o.numstring==3)and ("1"==serialData[5]):
                            for c in circles:
                                if c.state==0:
                                    c.init(3,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break
                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break

                        if (serialData[3]=="1") and (o.numstring==4)and ("1"==serialData[5]):
                            for c in circles:
                                if c.state==0:
                                    c.init(4,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break
                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break


                        if (o.numstring==6) and (serialData[0]=="1" and serialData[1]=="1") and ("1"==serialData[5]):
                    
                            for c in circles:
                                if c.state==0:
                                    c.init(1,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break
                                
                            for c in circles:
                                if c.state==0:
                                    c.init(2,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break  
                                
                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break

                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2+200,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break
                                
                        if (o.numstring==7) and (serialData[1]=="1" and serialData[2]=="1")and ("1"==serialData[5]):
                      
                            for c in circles:
                                if c.state==0:
                                    c.init(2,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break
                                
                            for c in circles:
                                if c.state==0:
                                    c.init(3,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break
                                
                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break

                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2+200,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break

                        if (o.numstring==8) and (serialData[2]=="1" and serialData[3]=="1")and ("1"==serialData[5]):
                           
                            for c in circles:
                                if c.state==0:
                                    c.init(3,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break

                            for c in circles:
                                if c.state==0:
                                    c.init(4,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break
                            
                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break

                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2+200,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break
                        
                    else:
                        
                        if (serialData[0]=="1") and (o.numstring==1) and (o.id==serialData[4]):
                            for c in circles:
                                if c.state==0:
                                    c.init(1,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break
                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break
                        if (serialData[1]=="1") and (o.numstring==2)and (o.id==serialData[4]):
                            for c in circles:
                                if c.state==0:
                                    c.init(2,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break
                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break

                        if (serialData[2]=="1") and (o.numstring==3)and (o.id==serialData[4]):
                            for c in circles:
                                if c.state==0:
                                    c.init(3,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break
                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break

                        if (serialData[3]=="1") and (o.numstring==4)and (o.id==serialData[4]):
                            for c in circles:
                                if c.state==0:
                                    c.init(4,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break
                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break

                        if (o.numstring==6) and (serialData[0]=="1" and serialData[1]=="1") and (o.id==serialData[4]):
                    
                            for c in circles:
                                if c.state==0:
                                    c.init(1,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break
                                
                            for c in circles:
                                if c.state==0:
                                    c.init(2,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break  
                                
                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break

                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2+200,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break
                                
                        if (o.numstring==7) and (serialData[1]=="1" and serialData[2]=="1")and (o.id==serialData[4]):
                      
                            for c in circles:
                                if c.state==0:
                                    c.init(2,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break
                                
                            for c in circles:
                                if c.state==0:
                                    c.init(3,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break
                                
                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break

                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2+200,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break

                        if (o.numstring==8) and (serialData[2]=="1" and serialData[3]=="1")and (o.id==serialData[4]):
                           
                            for c in circles:
                                if c.state==0:
                                    c.init(3,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break

                            for c in circles:
                                if c.state==0:
                                    c.init(4,int(o.id))
                                    Score+=1
                                    o.state=0# arrow disappear explosion shows up
                                    break
                            
                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break

                            for e in explosions: # find a explosion with state 0 and turn state into 1
                                if(e.state==False):
                                    e.init(o.pos[0]+o.pos[2]/2+200,o.pos[1]+o.pos[3]/2, o.color)
                                    e.state=True
                                    break
                    
                        

        ##draw explosion##
        for e in explosions:
            if(e.state):
                e.move()
                e.draw_stars(screen,level)

        ##draw circles##
        for c in circles:
            if(c.state==1):
                c.expand()
                c.draw(screen,level)

        ##generate arrows##
        elapsed = (time.time() - start)
        for i in xrange(len(arrowTime)):
            if((abs(elapsed-arrowTime[i]+1.2)<0.01) and (arrowTime[i] not in timeSet)):
                timeSet.add(arrowTime[i])
                for o in objects:
                    if (o.state==0):
                        if(directions[i]==1):
                            o.init(up, numString[i], 0, FallingSpeed, (0,255,0),"1")# which string and what direction
                        elif(directions[i]==2):
                            o.init(down, numString[i], 0, FallingSpeed, (255,0,0),"2")# which string and what direction
                        elif(directions[i]==3):
                            o.init(up2, numString[i], 0, FallingSpeed, (0,255,0),"1")# which string and what direction
                        else:
                            o.init(down2, numString[i], 0, FallingSpeed, (255,0,0),"2")# which string and what direction
                        o.state=1
                        break

        if(elapsed-arrowTime[-1])>3:
            gameover.main(Score,len(arrowTime))
            isQuit=True
            #show the score and result
            return True
            


        
        pygame.display.update()
        
        


