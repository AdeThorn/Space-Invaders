import sys
import pygame
import os
import random
import time


#general setup 
pygame.init()
clock=pygame.time.Clock()

#set up main window
WIDTH, HEIGHT = 750, 750
SCREEN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Space Invaders")


# Load images// loading images return surface objects
OCTOPUS = pygame.transform.scale(pygame.image.load(os.path.join("assets", "octopus.png")),(70,50))
ALIEN = pygame.transform.scale(pygame.image.load(os.path.join("assets", "alien.png")),(70,50))
UFO = pygame.transform.scale(pygame.image.load(os.path.join("assets", "ufo.png")),(70,50))

# Player player
PLAYER_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "spPlayer.png")),(70,50))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))


#background
BG=pygame.transform.scale(pygame.image.load(os.path.join("assets", "background.png")),(WIDTH,HEIGHT))

class Ship():
    def __init__(self,x,y,vel,cooldown_max,model,laser_vel):
        ships={"player":PLAYER_SHIP,"octopus":OCTOPUS,"alien":ALIEN,"ufo":UFO}
        self.x=x
        self.y=y
        self.vel=vel
        self.cooldown=0
        self.cooldown_max=cooldown_max
        self.model=ships[model]
        self.width=self.model.get_width()
        self.height=self.model.get_height()
        self.lasers=[]
        self.l_vel=laser_vel
        self.mask= pygame.mask.from_surface(self.model)
        self.rect = self.model.get_rect()
    
    def draw(self,screen):
        screen.blit(self.model,(self.x,self.y))
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
    
    #if player hit
    def hit(self):
        i=0 #pause and flash white screen
        hitScreen=pygame.Surface((WIDTH,HEIGHT))
        hitScreen.fill((255,0,0))
        hitScreen.set_alpha(3)
        while i < 50:
            SCREEN.blit(hitScreen,(0,0))
            pygame.display.update()
            pygame.time.delay(10)
            i+=1
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    i=51
                    pygame.quit()


        

        

class Enemy(Ship):

    def __init__(self,x,y,model):
        if model=="octopus":
            laser_vel=6
            ship_vel=3
            cooldown_max=12
            self.score=10
            self.laser_col=RED_LASER
        elif model=="alien":
            laser_vel=7
            ship_vel=4
            cooldown_max=12
            self.score=15
            self.laser_col=YELLOW_LASER
        elif model=="ufo":
            laser_vel=8
            ship_vel=6
            cooldown_max=9
            self.score=30
            self.laser_col=BLUE_LASER
        super().__init__(x,y,ship_vel,cooldown_max,model,laser_vel)
    
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
    def collide_with_player(self,player):
        offset=(player.x-self.x,player.y-self.y)
        #offset=(self.x-player.x,self.y-player.y)
            
        return self.mask.overlap(player.mask,offset)
        

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
        offset=(ship.x-self.x,ship.y-self.y) 
        return self.mask.overlap(ship.mask,offset)
        
def main_game_loop(username):

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
                x=random.randint(1,WIDTH-75)
                enemy=Enemy(x,-2,random.choice(["octopus","alien"]))
                enemies.append(enemy)

            #SPAWN UFO ENEMY VERY RARELY and only if above level 5
            if level>=5:
                toSpawnUfo=random.randint(1,100)
                if toSpawnUfo<=5:
                    x=random.randint(1,WIDTH-55)
                    enemy=Enemy(x,-2,"ufo")
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
            #check if enemy collides ith player
            if enemy.collide_with_player(player):
                lives-=1
                player.hit()
                enemies.remove(enemy) #destroy enemy ship
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
                    player.hit()
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
            save_score(username,score)
            lost_screen(username)
     
        #updating window
        pygame.display.flip()

def lost_screen(username):
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
                    main_game_loop(username)

def save_score(username,score):
    insertNotFound=True  #flag to see whether to log linenumber to insert at 
    with open('scoreStorage.csv','r') as f:
        newLines=[]
        insertAtLine=-1 #dummy value to see if should be updating score storage
        #current top 5 scores
        for linenum in range(5):
            prevInfo=f.readline()
            newLines.append(prevInfo)
            if prevInfo!='':
                prevScore=int(prevInfo.split(',')[1])
                if score>=prevScore and insertNotFound:
                    insertAtLine=linenum
                    insertNotFound=False
            else: #if prev info==''
                if insertNotFound: 
                    insertAtLine=linenum
                    insertNotFound=False

    if insertAtLine != -1:    
        newLines.insert(insertAtLine,f'{username},{score}\n')
        newLines.pop(5) #keep number of lines in storage at 5
        
        #update scoreStorage
        with open('scoreStorage.csv','w+') as f:
            for line in newLines:
                f.write(line)

def username_screen():
    font = pygame.font.SysFont('comicsans',30,True)
    enterName=font.render('ENTER USERNAME:',1, (255,255,255) )
    typingFlash=0 #variable to track when to flash '|'
    onScreen=True
    username=''
    while onScreen:
        typingFlash+=1
        SCREEN.blit(BG,(0,0))
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            #updating username as user types
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    onScreen=False
                if event.key==pygame.K_RETURN and username!='':
                    main_game_loop(username)
                elif event.key==pygame.K_BACKSPACE:
                    username=username[:-1]
                else:
                    username+=event.unicode
        #render username as it is typed
        userText=font.render(username,1,(255,255,255))
        typingPipe=font.render('|',1,(255,255,255))
        flashOn=typingFlash%30
        if flashOn<=20:
            SCREEN.blit(typingPipe,(480+userText.get_width(),348))
            
        SCREEN.blit(enterName,(250,350))
        SCREEN.blit(userText,(480,350))
        pygame.display.flip()
        clock.tick(60)

def start_menu():
    run=True
    font = pygame.font.SysFont('comicsans',30,True)
    hScoreText=font.render('HI-SCORE',1, (255,255,255) )
    playText=font.render('PLAY',1, (255,255,255) )
    titleText=font.render('SPACE INVADERS REBOOT',1, (255,255,255) )
    nameText=font.render('NAME',1, (255,255,255) )
    scoreText=font.render('SCORE',1, (255,255,255) )
    scoreTableText=font.render('*SCORE TABLE*',1, (255,255,255) )
    pointsText10=font.render('=10 POINTS',1, (255,255,255) )
    pointsText15=font.render('=15 POINTS',1, (255,255,255) )
    pointsText30=font.render('=30 POINTS',1, (255,255,255) )
    play_button=pygame.Rect(340,340,60,20)
    #Get 5 highest scores ever
    hScores=[]
    with open('scoreStorage.csv','r') as f:
        for num in range(5):
            line=f.readline()
            if line=='':
                break
            else:
                #add tuple of username and score
                prevInfo=line.split(',')
                prevScore=prevInfo[1].split()[0]
                hScores.append((prevInfo[0],prevScore))
    
    while run:
        SCREEN.blit(BG,(0,0))
        SCREEN.blit(hScoreText,(330,10))
        SCREEN.blit(nameText,(130,10))
        SCREEN.blit(scoreText,(550,10))
        i=0
        for info in hScores:
            i+=1
            infoName=font.render(info[0],1,(255,255,255))
            SCREEN.blit(infoName,(140,10+(i*30)))
            infoScore=font.render(info[1],1,(255,255,255))
            SCREEN.blit(infoScore,(580,10+(i*30)))

        pygame.draw.rect(SCREEN,(0,0,0),play_button)
        SCREEN.blit(playText,(340,340))
        SCREEN.blit(titleText,(230,390))
        SCREEN.blit(scoreTableText,(290,460))
        SCREEN.blit(OCTOPUS ,(330,500))
        SCREEN.blit(pointsText10,(400,515))
        SCREEN.blit(ALIEN,(330,550))
        SCREEN.blit(pointsText15,(400,565))
        SCREEN.blit(UFO ,(330,600))
        SCREEN.blit(pointsText30,(400,615))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    run=False
            #checking if clicked play button
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if play_button.collidepoint(pygame.mouse.get_pos()):
                    run=False
                    username_screen()

start_menu()