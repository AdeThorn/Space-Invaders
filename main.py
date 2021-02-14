import sys
import pygame
import os
import random
import time
##TODO
## implement enemies strafing
#make number of bullets max of them limited
#have blue shoot when player in small range, green in larger range and red completely random
#blue is rare villian
# implement collisions
# implement health
# implement losing lives
#implement levels
#implement scores
#implement playing with username 
#implement top 10 highscores on loading screen
#everyround up laser velocity by 1??


#general setup 
pygame.init()
clock=pygame.time.Clock()

#set up main window
WIDTH, HEIGHT = 750, 750
SCREEN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Space Invaders")


# Load images// loading images return surface objects
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Player player
PLAYER_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))


#background
BG=pygame.transform.scale(pygame.image.load(os.path.join("assets", "background.png")),(WIDTH,HEIGHT))

class Ship():
    def __init__(self,x,y,vel,cooldown_max,img,laser_vel):
        ships={"player":PLAYER_SHIP,"red":RED_SPACE_SHIP,"green":GREEN_SPACE_SHIP,"blue":BLUE_SPACE_SHIP}
        self.x=x
        self.y=y
        self.vel=vel
        self.cooldown=0
        self.cooldown_max=cooldown_max
        self.img=ships[img]
        self.width=self.img.get_width()
        self.height=self.img.get_height()
        self.lasers=[]
        self.l_vel=laser_vel
    
    def draw(self,screen):
        screen.blit(self.img,(self.x,self.y))
        for laser in self.lasers:
            laser.draw(SCREEN)
    
    def shoot(self):
        if self.cooldown==0:
            self.lasers.append(Laser(round(self.x),round(self.y-self.height//2),GREEN_LASER,self.l_vel))
            self.cooldown=1

        if self.cooldown>0:
            self.cooldown+=1
        if self.cooldown>self.cooldown_max:
            self.cooldown=0


class Player(Ship):
    def __init__(self,x,y):
        super().__init__(x,y,6,8,"player",-8)

        

        

class Enemy(Ship):

    def __init__(self,x,y,color):
        if color=="red":
            laser_vel=14
            ship_vel=6
            cooldown_max=5
        elif color=="green":
            laser_vel=10
            ship_vel=8
            cooldown_max=5
        elif color=="blue":
            laser_vel=25
            ship_vel=15
            cooldown_max=5
        super().__init__(x,y,ship_vel,cooldown_max,color,laser_vel)
    
    def push(self):
        self.y+=self.vel

    
class Laser():

    def __init__(self,x,y,img,vel):
        self.x=x
        self.y=y
        self.img=img
        self.vel=vel

    def draw(self,screen):
        screen.blit(self.img,(self.x,self.y))

   

def main_game_loop():

    #game variables
    lives=0
    level=1
    levelup=True
    player=Player(200,200)
    enemies=[]
    timeToSpawn=random.randint(3,4)
    spawnYet=False
    spawnTimes=[] #list of times to spawn relative to current time i.e 1 sec from now,3 sec from now

    def redraw_screen():
        SCREEN.blit(BG,(0,0)) #filling screen with baackground image at position 0,0
        player.draw(SCREEN)
        for enemy in enemies:
            enemy.draw(SCREEN)

    def spawnEnemy(currentTime,spawnTimes,timeToSpawn,spawnYet):

        if currentTime>timeToSpawn:
            spawnYet=False
            
            if len(spawnTimes)!=0:
            #timetospawn got from current time + random index in spawntimes list
                timeToSpawn=currentTime+(spawnTimes.pop(random.randint(0,len(spawnTimes)-1)))
            

        elif currentTime==timeToSpawn and spawnYet==False:
            #spawn enemy off map 
            #SPAWN blue ENEMY VERY RARELY
            x=random.randint(1,WIDTH-10)
            enemy=Enemy(x,-2,random.choice(["green","red"]))
            enemies.append(enemy)
            spawnYet=True

        return [timeToSpawn,spawnYet]
        

    #game loop
    run=True
    while run:
        clock.tick(60)
        redraw_screen()
        
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    run=False
        
        ######################LEVEL UP VARIABLES#####################
        if levelup:
            if level<5:
                amount=20
                timeBound=6   #upperbound for randrange
                amountAtOnce=2 #max amount of enemies to spawn at one time
            elif level>5 and level<15:
                amount=35
                timeBound=4
                amountAtOnce=3
            else:
                amount=50
                timeBound=3
                amountAtOnce=4
            #compute relative times to spawn enemies
            for num in range(amount):
                spawnTimes.append(random.randrange(timeBound))
            levelup=False
        
        #check if time to spawn enemy
        currentTime=pygame.time.get_ticks()//1000
        if currentTime>=timeToSpawn:
            timeToSpawn,spawnYet=spawnEnemy(currentTime,spawnTimes,timeToSpawn,spawnYet)  #returns next time to spawn and spawnYet
       
        ######################MOVING PLAYER#####################
        keys=pygame.key.get_pressed()
        
        if keys[pygame.K_a] and player.x>player.vel:
            player.x-=player.vel

        elif keys[pygame.K_d] and player.x+player.vel+player.width<WIDTH-player.vel:
            player.x+=player.vel

        if keys[pygame.K_s] and player.y +player.vel + player.height< HEIGHT:
            player.y+=player.vel

        elif keys[pygame.K_w] and player.y>0+player.vel:
            player.y-=player.vel
        
        #shooting laser
        if pygame.mouse.get_pressed()[0]: 
            player.shoot()


        for enemy in enemies:
            enemy.push()
       ######################MAINTENANCE#####################
        if len(enemies)==0 and len(spawnTimes)==0:
            levelup=True
            level+=1

        #make sure laser either on screen or deleted
        for laser in player.lasers:
            if laser.y < HEIGHT and laser.y>0:
                laser.y +=laser.vel
            else:
                #delete laser
                player.lasers.pop(player.lasers.index(laser))

        #updating window
        pygame.display.flip()

main_game_loop()