import sys
import pygame
import os
import random
import time
##TODO


#have blue shoot when player in small range, green in larger range and red completely random

#implement player collision with enemy
#implement playing with username 
#implement main menu
#implement top 10 highscores on loading screen
## implement enemies strafing after
#every couple rounds up laser velocity by 1?? 
#implement this later: hold all enemy lasers in 1 list so that when enemy dies its lasers arent removed from screen as well 
# and collisions between alsers


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
        self.mask= pygame.mask.from_surface(self.img)
        self.rect = self.img.get_rect()
    
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
            laser_vel=6
            ship_vel=3
            cooldown_max=12
            self.score=10
            self.laser_col=RED_LASER
        elif color=="green":
            laser_vel=7
            ship_vel=4
            cooldown_max=12
            self.score=15
            self.laser_col=YELLOW_LASER
        elif color=="blue":
            laser_vel=8
            ship_vel=6
            cooldown_max=9
            self.score=30
            self.laser_col=BLUE_LASER
        super().__init__(x,y,ship_vel,cooldown_max,color,laser_vel)
    
    def push(self):
        self.y+=self.vel

    def shoot(self):
        if self.cooldown==0:
            self.lasers.append(Laser(round(self.x),round(self.y-self.height//2),self.laser_col,self.l_vel))
            self.cooldown=1

        if self.cooldown>0:
            self.cooldown+=1
        if self.cooldown>self.cooldown_max:
            self.cooldown=0

class Laser():

    def __init__(self,x,y,img,vel):
        self.x=x
        self.y=y
        self.img=img
        self.vel=vel
        self.mask=pygame.mask.from_surface(img)
        self.rect = self.img.get_rect()
        self.width=self.img.get_width()
        self.height=self.img.get_height()

    def draw(self,screen):
        screen.blit(self.img,(self.x,self.y))

    def hit(self,ship):
        if type(ship)==Enemy:
            offset=((self.x)-(ship.x-ship.width//2),self.y-(ship.y-ship.height//2))

        elif type(ship)==Player:
            offset=(self.x-ship.x,self.y-ship.y)
            
        return self.mask.overlap(ship.mask,offset)
        



   

def main_game_loop():

    #game variables
    font = pygame.font.SysFont('comicsans',30,True)
    lives=3
    score=0
    level=1
    levelup=False
    player=Player(250,500)
    enemies=[]
    timeToSpawn=random.randint(3,4)
    spawnYet=False
    spawnTimes=[] #list of times to spawn relative to current time i.e 1 sec from now,3 sec from now
    for num in range(10):
        spawnTimes.append(random.randrange(6)) #time to spawn enemies for 1st round
    amountAtOnce=2 #max amount of enemies can spawn at same time for round 1 to 5
    startNextRound=0 #dummy value so starNExtRound is declared before use
    calculatedNextRoundTime=False

    #function for when you lose a life pause screen then restart round
    def lose_life():
        pass
    def redraw_screen():
        SCREEN.blit(BG,(0,0)) #filling screen with baackground image at position 0,0
        player.draw(SCREEN)
        for enemy in enemies:
            enemy.draw(SCREEN)

        livesText=font.render('LIVES: '+ str(lives),1,(255,255,255))
        scoreText=font.render('SCORE: '+ str(score),1,(255,255,255))
        levelText=font.render('LEVEL: '+ str(level),1, (255,255,255) )
        SCREEN.blit(livesText,(650,10))
        SCREEN.blit(scoreText,(5,10))
        SCREEN.blit(levelText,(5,HEIGHT-20))

    def spawnEnemy(currentTime,spawnTimes,timeToSpawn,spawnYet,amountAtOnce):
        if currentTime>timeToSpawn:
            spawnYet=False
            
            if len(spawnTimes)!=0:
            #timetospawn got from current time + random index in spawntimes list
                timeToSpawn=currentTime+(spawnTimes.pop(random.randint(0,len(spawnTimes)-1)))
            

        elif currentTime==timeToSpawn and spawnYet==False:
            
            
            #determine how many enemies to spawn at same time
            amountToSpawn=random.choice(range(1,amountAtOnce+1))
            for num in range(amountToSpawn):
                #spawn enemy off map 
                x=random.randint(1,WIDTH-55)
                enemy=Enemy(x,-2,random.choice(["green","red"]))
                enemies.append(enemy)

            #SPAWN blue ENEMY VERY RARELY and only if above level 5
            if level>=5:
                toSpawnBlue=random.randint(1,100)
                if toSpawnBlue<=5:
                    x=random.randint(1,WIDTH-55)
                    enemy=Enemy(x,-2,"blue")
                    enemies.append(enemy)

            spawnYet=True

        return [timeToSpawn,spawnYet]
    
    #screen maintenance and level maintenance
    def maintenance():
        nonlocal levelup,calculatedNextRoundTime,lives,score

        if len(enemies)==0 and len(spawnTimes)==0:
            levelup=True
            
            if not calculatedNextRoundTime:
                 #Wait 2 seconds before starting to spawn enemies again
                startNextRound=pygame.time.get_ticks()//1000 + 2
                calculatedNextRoundTime=True
        #check if enemy is hit
        for enemy in enemies:
            for laser in player.lasers:
                if laser.hit(enemy):
                    player.lasers.remove(laser)
                    score+=enemy.score
                    enemies.remove(enemy)
            enemy.push()
            
            if enemy.y> HEIGHT:
                lives-=1
                enemies.remove(enemy)

            #shoot ~20% of the time
            toShoot=random.randint(1,10)
            if toShoot<=2 and len(enemy.lasers)<=4:
                enemy.shoot()

            #check if player is hit
            for laser in enemy.lasers:
                if laser.hit(player):
                    enemy.lasers.remove(laser)
                    lives-=1
                if laser.y < HEIGHT and laser.y>0:
                    laser.y +=laser.vel
                else:
                #delete laser if off screen
                    enemy.lasers.remove(laser)

        #make sure player laser either on screen or deleted
        for laser in player.lasers:
            if laser.y < HEIGHT and laser.y>0:
                laser.y +=laser.vel
            else:
                #delete laser
                player.lasers.pop(player.lasers.index(laser))

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
        if levelup and pygame.time.get_ticks()//1000>=startNextRound:
            calculatedNextRoundTime=False
            level+=1
            
            if level<5:
                amount=10
                timeBound=7   #upperbound for randrange
                amountAtOnce=2 #max amount of enemies to spawn at one time
            elif level>5 and level<15:
                amount=15
                timeBound=4
                amountAtOnce=3
            else:
                amount=20
                timeBound=3
                amountAtOnce=3
            #compute relative times to spawn enemies
            for num in range(amount):
                spawnTimes.append(random.randrange(timeBound))
            levelup=False
        
        #check if time to spawn enemy
        currentTime=pygame.time.get_ticks()//1000
        if currentTime>=timeToSpawn:
            timeToSpawn,spawnYet=spawnEnemy(currentTime,spawnTimes,timeToSpawn,spawnYet,amountAtOnce)  #returns next time to spawn and spawnYet
       
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


        maintenance()

        if lives==0:
            run=False
            lost_screen()
     
        #updating window
        pygame.display.flip()

def lost_screen():
    run=True
    while run:
        font = pygame.font.SysFont('comicsans',30,True)
        failedText=font.render('MISSION FAILED',1, (255,255,255) )
        clickText=font.render('CLICK ANYWHERE TO START AGAIN',1, (255,255,255) )
        SCREEN.blit(BG,(0,0))
        SCREEN.blit(failedText,(300,20))
        SCREEN.blit(clickText,(200,400))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    run=False
            if event.type==pygame.MOUSEBUTTONDOWN:
                if event.button==1:
                    run=False
                    main_game_loop()

main_game_loop()