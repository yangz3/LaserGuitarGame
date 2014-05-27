import os, pygame, sys
from pygame.locals import *
sys.path.insert(0,'./lib/')
import menu,levelinputbox
import wave
import sys
from pylab import * # this is part of  matplotlib and I have already installed that.
import numpy 
import scipy
import copy
from scipy.signal import argrelextrema
import random
import tkFileDialog
from Tkinter import Tk
#import everything
import threading
import ctypes
import time, random, math, serial
import os, sys, pygame
from pygame.locals import *
import gameover
 


#------------------------------------CONSTANTS------------------------------------#

FPS = 120
WINDOWWIDTH = 1000
WINDOWHEIGHT = 800
CELLSIZE = 10
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)
highThredPerCent=100

FallingSpeed=3
WindowHeight=800
WindowWidth=1024
NUMSTARS=5
MaxNumOfExplosions=5
MaxNumOfArrows=5
MaxNumOfCircles=5


#Colors       R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR = BLACK



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
        if(True):
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




def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(SCREEN, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(SCREEN, DARKGRAY, (0, y), (WINDOWWIDTH, y))
def terminate(isQuit):
    pygame.quit()
    #startGame.serial_port.close()
    isQuit[0]=1


def load(path,level):
  
    Tk().withdraw()
    path[0] = tkFileDialog.askopenfilename(initialdir="musics",title="Choose your favorite song!")
    fail = False
    try:
        mapx = open(path[0])
    except: 
        print('Could not find file... location:{}'.format(path[0]))
        fail = True
    if not fail:
        mapx.close()
# do something to the wav file
        audioAnalysis(path[0],level)
        print "load file done!!"
        pygame.display.update()


def levelload(level):
    
    l = levelinputbox.ask(SCREEN, "Choose level between 1 to 3")
    l = int(l)
    fail = False
    if l not in xrange(1,4):
        print("Wrong Number")
        fail = True
    else:
        level[0] = l
        print "Choose level done!!"
        pygame.display.update()


###############   smooth  ##################################
def smoothTriangle(data,degree,dropVals=False):
        triangle=numpy.array(range(degree)+[degree]+range(degree)[::-1])+1
        smoothed=[]
        for i in range(degree,len(data)-degree*2):
                point=data[i:i+len(triangle)]*triangle
                smoothed.append(sum(point)/sum(triangle))
        if dropVals: return smoothed
        smoothed=[smoothed[0]]*(degree+degree/2)+smoothed
        while len(smoothed)<len(data):smoothed.append(smoothed[-1])
        return smoothed

def audioAnalysis(path,level):
    try:
        lowThredPerCent=15+abs(level-3)*15 # difficulty control
    except:
        lowThredPerCent=15+abs(2-3)*15 # defalt setting difficulty is 2
    LowThred=0.2
    HighThred=0.6
    filename=path
    a = pygame.mixer.Sound(filename)
    stringUnits=[[2,3,4,1,2,3],
            [1,2,3,2,3,4],
            [1,3,2,4],
            [4,2,3,1],
            [1,2,3,4],
            [4,3,2,1],
            [6,7,8], # trick: after %5, the result is the num of String  
            [6,7,8],
            [8,7,6],
            [8,7,6]
            ]
    dirUnits=[[2,1,2,2,1,2],
            [2,1,2,2,1,2],
            [1,1,1,1],
            [2,2,2,2],
            [1,2,1,2],
            [2,1,2,1],
            [3,3,3],
            [4,4,4],
            [3,3,3],
            [4,4,4]
            ]

########################    basic info of raw data    ##############################

    Wave_read=wave.open(filename,"r")
    print "Frame rate: " + str (Wave_read.getframerate())
    print "Sample width: "+ str(Wave_read.getsampwidth())
    print "Total frames: "+str(Wave_read.getnframes())

########################    sample the raw data    ###############################
    bytesThing= Wave_read.readframes(-1)# -1 means all of the frames
    sound_info = fromstring(bytesThing, 'int16') # from byte strings to int value
    reducedSound_info=sound_info[::300] # decrease the sample rate to 1% of original one


####################### fft band pass filter #####################################
    fft=scipy.fft(reducedSound_info)
    mir = len(reducedSound_info)/2
    bp=copy.deepcopy(fft)
    for i in range(len(bp)):
        if i<=mir+LowThred*mir or i>=mir+HighThred*mir:bp[i]=0
    ibp=scipy.ifft(bp)

####################### moving triangle smooth #####################################
    sibp=smoothTriangle(abs(ibp),30)

####################### moving window peak ditection #####################################
    nsibp=numpy.asarray(sibp)
    peaks=argrelextrema(nsibp, numpy.greater, 0,200)
    peaks=peaks[0].tolist()
    #print peaks

###################### filter the peaks with bottom quartile ##################
    afterThredPeaks=copy.deepcopy(peaks)
    peaksValue=[]
    for i in peaks:
        peaksValue.append(nsibp[i])
    lowThred=numpy.percentile(peaksValue,lowThredPerCent)
    highThred=numpy.percentile(peaksValue,highThredPerCent)
    for i in peaks:
        if(nsibp[i]<lowThred):
            afterThredPeaks.remove(i)
        if(nsibp[i]>highThred):
            afterThredPeaks.remove(i) 
    print afterThredPeaks

########################    write data to file    ##################################
    lenData=float(len(sibp))
    lenMusic=a.get_length()
    WriteFile ="tempo.txt"
    File = open(WriteFile, "w")
    ## write the the num of string with random combination of unit###########
    pointer=0
    whichUnit=random.randint(0,(len(stringUnits)-1))
    for i in xrange(len(afterThredPeaks)):
        if pointer>= len(stringUnits[whichUnit]):# this unit is done, change to another unit
            whichUnit=random.randint(0,(len(stringUnits)-1))
            pointer=0
        print >> File, (str(lenMusic*afterThredPeaks[i]/lenData)+" "+str(stringUnits[whichUnit][pointer])+" "+str(dirUnits[whichUnit][pointer]))
        pointer+=1
    File.close()
    Wave_read.close()




def main():
    global FPSCLOCK, SCREEN, BASICFONT, gol
    level=[None]
    path=[None]
    isQuit=[0]
    
    #Init pygame
    pygame.init()
    pygame.display.init 
    pygame.mixer.init()
    
    FPSCLOCK = pygame.time.Clock()
    #Window initializations
    icon = pygame.image.load("resources/images/favicon.png")
    pygame.display.set_icon(icon)
    pygame.display.set_caption('GG')
    SCREEN = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    
    #Setting some fitting music
    pygame.mixer.music.load("resources/music/music2.mp3")
    pygame.mixer.music.play()



    ## thread ###################################
    #thread=StoppableThread(target=read_from_port, args=(serial_port,))

    t = threading.Thread(target=read_from_port, args=(serial_port,))
    #thread.daemon = True
    t.setDaemon(True)
    t.start()
    #t.join()
    
    while isQuit[0]!=1:
        print "r"
        mainmenu(icon,level,path,isQuit)



def mainmenu(icon,level,path,isQuit):
  
    SCREEN.fill(BGCOLOR)
    drawGrid()
    pygame.display.update()
    pygame.display.set_caption('Menu')
    font = pygame.font.Font(None,80)
    text = font.render("Guitar Game", 20,(WHITE))
    SCREEN.blit(text,(10,10))
    SCREEN.blit(icon, (350,150))

    if level[0]!=None and path[0]!=None:
        option = menu.menu(SCREEN, 
                      ['Start','Level: %d' % level[0],'Load: %s' % path[0].split("/")[-1] ,'Exit'],
                      128,128,None,64,1.2,WHITE,RED)
    elif level[0]!=None:
        option = menu.menu(SCREEN, 
                      ['Start','Level: %d' % level[0],'Load','Exit'],
                      128,128,None,64,1.2,WHITE,RED)
    elif path[0]!=None:
        option = menu.menu(SCREEN, 
                      ['Start','Level: %d','Load: %s' % path[0].split("/")[-1],'Exit'],
                      128,128,None,64,1.2,WHITE,RED)
    else:
        option = menu.menu(SCREEN, 
                      ['Start','Level','Load' ,'Exit'],
                      128,128,None,64,1.2,WHITE,RED)

    if option == -1:
        terminate(isQuit)
    if option == 0:     
        if path[0]!=None and level[0]!=None:
            pygame.mixer.music.stop()
            option = 0
            print level[0]
            #################### startGame ####################
            main2(path[0],level[0],path[0].split("/")[-1])
            
            level[0]=None
            path[0]=None
            isQuit[0]=0
            
            #terminate(isQuit)
        else:
            print "Please choose level and load a music first"
            
    elif option == 1:
        levelload(level)
        option = 0
            
    elif option == 2:
        if level[0]!= None:
            load(path,level[0])
        else:
            level[0]=2
            load(path,level[0])
        option = 0
            
    elif option == 3:
        terminate(isQuit)

def main2(filename,level,whichMusic):
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




    

    

if __name__ == '__main__':
    main()
