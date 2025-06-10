import pygame
import os
import time
import json
import random
from pygame import mixer
# high_score = 0
pygame.font.init()
mixer.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter Game ")


# ALIEN_SHIP
ALIEN_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "alienShip.png")),(70, 45)).convert_alpha()

# Player player
PLAYER_SPACE_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "spaceship.png")),(150,100)).convert_alpha()
# PLAYER_SPACE_SHIP = pygame.image.load(os.path.join("assets", "spaceship.png")).convert_alpha()

# loading asteroids
SMALL_ASTEROIDS = pygame.image.load(os.path.join("assets", "asteroid50.png")).convert_alpha()
MEDIUM_ASTEROIDS = pygame.image.load(os.path.join("assets", "asteroid100.png")).convert_alpha()

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png")).convert_alpha()
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png")).convert_alpha()
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png")).convert_alpha()
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png")).convert_alpha()

# POWER UPS
POWER_UP_HEALTH = pygame.transform.scale(pygame.image.load(os.path.join("assets", "powerup_heart.png")),(80, 80)).convert_alpha()

POWER_UP_LASER = pygame.image.load(os.path.join("assets", "gift.png")).convert_alpha()
COLLIDE_POWER_UP = pygame.image.load(os.path.join("assets", "no-damage-powerup.png")).convert_alpha()
SHEILD = pygame.transform.scale(pygame.image.load(os.path.join("assets", "sheild-ship.png")),(100,100)).convert_alpha()

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "starbg.png")), (WIDTH, HEIGHT)).convert_alpha()
# Button Class from which buttons for meny and options are
class Button:
        def __init__(self, image, pos, text_input, font, base_color, hovering_color):
            self.image = image
            self.x_pos = pos[0]
            self.y_pos = pos[1]
            self.font = font
            self.base_color, self.hovering_color = base_color, hovering_color
            self.text_input = text_input
            self.text = self.font.render(self.text_input, True, self.base_color)
            if self.image is None:
                self.image = self.text

            self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
            self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))
            if text_input == "":
                self.text_rect = self.rect
        # updates the button on screen
        def update(self, screen):
            if self.image is not None:
                screen.blit(self.image, self.rect)
            screen.blit(self.text, self.text_rect)
        # checks if user gave an input / clicked the button
        def checkForInput(self, position):
            if position[0] in range(self.text_rect.left, self.rect.right) and position[1] in range(self.text_rect.top, self.text_rect.bottom):
                return True
            return False
        # changer the color of the button when user hovers over it.
        def changeColor(self, position):
            if position[0] in range(self.text_rect.left, self.text_rect.right) and position[1] in range(self.text_rect.top, self.text_rect.bottom):
                self.text = self.font.render(self.text_input, True, self.hovering_color)
            else:
                self.text = self.font.render(self.text_input, True, self.base_color)

# class Powerup:
class Powerup:
    def __init__(self, x, y,type):
        # self.powerup_img = self.POWER_MAP[type]
        self.powerup_img = None
        self.x = x
        self.y = y
        self.type = type
    #     speed at which power up comes down
    def move(self, vel):
        self.y += vel
    # makes the powerup appear on screen
    def draw(self, window):
        window.blit(self.powerup_img, (self.x, self.y))
    # Returns the width of  power image
    def get_width(self):
        return self.powerup_img.get_width()
    # Returns the heigth of powerup image
    def get_height(self):
        return self.powerup_img.get_height()
    # checks if powerup collides with something(player ship)
    def collision(self, obj):
        return collide(self, obj)


# This class makes the health power up which gives user one  life
class HealthPowerup(Powerup):
    def __init__(self, x, y):
        super().__init__(x,y,type)
        self.type = 'health'
        self.powerup_img = POWER_UP_HEALTH
        self.mask = pygame.mask.from_surface(self.powerup_img)



# the power up allows user to shoot bullets at rapid speed
class InfiniteShootPowerup(Powerup):
    def __init__(self, x, y):
        super().__init__(x,y,type)
        self.type = 'infiniteshoot'
        self.powerup_img = POWER_UP_LASER
        self.mask = pygame.mask.from_surface(self.powerup_img)


    # impliment the infinate shoot power up
    def effect(self):
        # setting the shooting cooldown to zero
        Ship.COOLDOWN = 0
        return pygame.time.get_ticks()
#     Powerup that doesn't reduces health when it collides with laser, asteroids, enemyship
class ColidePowerup(Powerup):
    def __init__(self, x, y):
        super().__init__(x, y, type)
        self.type = 'noCollideDamage'
        self.powerup_img = COLLIDE_POWER_UP
        self.mask = pygame.mask.from_surface(self.powerup_img)
# Class that makes asteroids
class Asteroids:
    SIZE_MAP = {
                "small": SMALL_ASTEROIDS,
                "medium": MEDIUM_ASTEROIDS,
                }
    def __init__(self, x, y, size):
        self.asteroid_img = self.SIZE_MAP[size]
        self.mask = pygame.mask.from_surface(self.asteroid_img)
        self.x = x
        self.y = y
    def move(self, vel):
        self.y += vel
    def draw(self, window):
        window.blit(self.asteroid_img, (self.x, self.y))
    def get_width(self):
        return self.asteroid_img.get_width()

    def get_height(self):
        return self.asteroid_img.get_height()


# Class that makes lasers that player and enemy shoot
class Laser :
    def __init__(self,x,y ,img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

# Class that makes ship
class Ship :
    COOLDOWN = 40
    def __init__(self,x,y,health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
    # places the ship on window
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)
    #  Mehthod to control the laser that come out of the ship
    def move_lasers(self, vel, obj,damage):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= damage*10
                mixer.Sound('sounds/gettinghit.ogg').play() #Sound effect when enemy laser hits the player
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0 :
            laser = Laser(self.x+24,self.y+5,self.laser_img)
            mixer.Sound('sounds/shoot.ogg').play()
            self.lasers.append(laser)
            self.cool_down_counter = 1
    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()
# playership inherits from Ship class and makes the player ship
class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.name = ""
        self.ship_img = PLAYER_SPACE_SHIP
        self.laser_img = BLUE_LASER
        # MASK FOR PIXEL PERFECT COLLISOINN
        self.highscore = 0
        self.score = 0
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.shield = None
    # method that controls the laser movement comes out of the ship.
    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.score += 2
                        mixer.Sound('sounds/bangSmall.ogg').play()
                        if laser in self.lasers:
                            self.lasers.remove(laser)
    # method that draw the player on the screen
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
    #  method that makes helath bar appear below space ship
    def healthbar(self, window):
        pygame.draw.rect(window, (0, 255, 255), (
        self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health / self.max_health),
        10))
    # method to implement sheild on spaceship
    def sheild(self):
        self.ship_img = SHEILD
# class that makes the enemy spaceship
class Enemy(Ship):
    LASER_MAP = {
                "red": (ALIEN_SHIP, RED_LASER),
                "green": (ALIEN_SHIP, GREEN_LASER),
                "yellow": (ALIEN_SHIP, YELLOW_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.LASER_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    # method to move enemy ship down
    def move(self, vel):
        self.y += vel
    # method to shoot laser from enemy ship
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-17, self.y+10, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 0
# method to check collision between two object
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None
# function to store highscore in game
def file_score(mode=None,score=0):
    if mode == 'r':
        if not os.path.exists("hscore.json"):
            print("file not exsist")
            return score
        else :
            data = json.load(open("hscore.json"))
            return data['High Score']
    elif mode == 'w':
        with open("hscore.json", "w") as f:
            hscore = {'High Score': score}
            json.dump(hscore, f)

# funtion to save score for rankings
def add_score(player_name, score):
    # Read scores from file
    if not os.path.exists("scores.json"):
        with open("scores.json","w") as f :
            f.write("{}")
    with open("scores.json", "r") as f:
        scores = json.load(f)

    if player_name in scores :
        if scores[player_name] <= score:
            scores[player_name] = score
        else:
            pass
    else:
        scores[player_name] = score
    # Write updated scores to file
    with open("scores.json", "w") as f:
        json.dump(scores, f)

    print(f"Score added: {player_name}: {score}")

# main function that makes the objects of classes and is responsible for the functioning of the whole game
def main(player_name):
    run = True
    FPS = 60 # Frame rate of game
    clock = pygame.time.Clock()
    lost = False
    lost_count = 0
    level = 0 # game level
    lives = 3 # lives player start with
    laser_vel =17 #speed of shooting lasers
    enemies = []
    asteroids = []
    powerups = []
    enemy_ship_wave_number = 2 #enemy ship at start
    asteroid_wave_number = 10 #asteroids at start
    enemy_speed = 1 #enemy speed
    asteroid_speed = 1 #asteroid speed

    damage = 1 #damage per laser shoot (collsion has 10x the damage)
    # score = 0
    main_font = pygame.font.SysFont("comicsans",25)
    lost_font = pygame.font.SysFont("comicsans",40)
    player_speed = 8 # player ship movement speed
    player = Player(300,650)
    player.name = player_name
    effect_time_limit = 5000 #time power up remains active
    effect_timer_start = None
    player.highscore = file_score('r')
    #funtion that draws the frame every time called and places element
    def redraw_win():
        # print(player.name)
        WIN.blit(BG,(0,0))
        # draw text
        lives_label = main_font.render(f"LIVES : {lives}",1,(255,255,255))
        level_label = main_font.render(f"Level : {level}",1,(255,255,255))
        score_Label = main_font.render(f"Score : {player.score}",1,(255,255,255))
        highscore_label = main_font.render(f"High Score : {player.highscore}",1,(255,255,255))
        WIN.blit(lives_label,(10,10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(score_Label,(10,lives_label.get_height()+10))
        WIN.blit(highscore_label, (WIDTH - highscore_label.get_width() - 10, level_label.get_height()+10))
        #drawing enemies , asteroids and power ups
        for enemy in enemies :
            enemy.draw(WIN)  
        for asteroid in asteroids :
            asteroid.draw(WIN)
        for powerup in powerups:
            powerup.draw(WIN)
        # Draw player
        player.draw(WIN)
        # Checking if Player lost
        if lost:
            lost_label = lost_font.render("You lost !!!", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))
        pygame.display.update()

    while run :
        clock.tick(FPS)

        if player.health <= 0 and lives > 0  :
            lives -=1
            mixer.Sound('sounds/healthup.ogg').play()
            for i in range(player.max_health):
                player.health += 1
        redraw_win()
        if lives <= 0 or player.health <= 0 :
            # player.highscore = player.score #book1
            if player.score > player.highscore:
                file_score('w', player.score)
            lost = True
            lost_count += 1
        if lost:
            if lost_count > FPS * 3 :
                run  = False

                add_score(player.name,player.score)
            else :
                continue
        #checking if the user lost
        if lost :
            if lost_count > FPS * 3 :
                ranking_page()
                run = False
            else :
                continue
        # checking if user cleared the wave and leveling up and incrasing difficulty also increasing enemies
        if len(enemies) == 0 and len(asteroids) == 0:
            level +=1
            enemy_ship_wave_number +=2
            asteroid_wave_number +=5
            if  level%2 ==0  :
                # adding power ups to screen
                puhealth = HealthPowerup(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100))
                pulaser = InfiniteShootPowerup(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100))
                noCollided = ColidePowerup(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100))
                powerups.append(noCollided)
                powerups.append(puhealth)
                powerups.append(pulaser)
            # adding enemies to screen
            for i in range(enemy_ship_wave_number):
                enemy = Enemy(random.randrange(50,WIDTH-100),random.randrange(-1500,-100),random.choice(["red","yellow","green"]))
                enemies.append(enemy)
            # adding asteroids to screen
            for i in range(asteroid_wave_number):
                asteroid = Asteroids(random.randrange(50,WIDTH-100),random.randrange(-1500,-100),random.choice(["small","medium","small"]))
                asteroids.append(asteroid)
        # checking events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]  and player.x - player_speed > 0: #left
            player.x -= player_speed
        if keys[pygame.K_RIGHT]  and player.x - player_speed + player.get_width() < WIDTH: #Right
            player.x += player_speed
        if keys[pygame.K_UP]  and player.y - player_speed > 0: #Up
            player.y -= player_speed
        if keys[pygame.K_DOWN]  and player.y - player_speed + player.get_height() +30 < HEIGHT: #DOWN
            player.y += player_speed
        if keys[pygame.K_SPACE]:
            # making player shoot when space is pressed
            player.shoot()

        # keeping track of enemies and seeing if they got shot or got out off screen and removing them.
        for enemy in enemies[:] : # Colon is to create a copy list so it the list we are looping
            # moving enemies and lasers
            enemy.move(enemy_speed)
            enemy.move_lasers(laser_vel, player,damage)
            # Making enemy shoot at a random time
            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()
            # Checking if enemies collided with player
            if collide(enemy, player):
                mixer.Sound('sounds/bangLarge.ogg').play()
                player.health -= damage*10
                enemies.remove(enemy)
                #checking if enemy got out of screen
            elif enemy.y + enemy.get_height()> HEIGHT :
                lives -=1
                enemies.remove(enemy)
                # checking if asteroid collided with player or laser or got out of screen
        for asteroid in asteroids[:] : # Colon is to create a copy list so it the list we are looping over doesn't get modifies below
            asteroid.move(asteroid_speed)
            if collide(asteroid, player):
                player.health -= 10*damage
                mixer.Sound('sounds/bangLarge.ogg').play()
                asteroids.remove(asteroid)

            elif asteroid.y + asteroid.get_height()> HEIGHT :
                lives -= 1
                asteroids.remove(asteroid)
                #checking if powerup collided with player or got our of screen
        for powerup in powerups[:] : # Colon is to create a copy list so it the list we are looping over doesn't get modifies below
            powerup.move(asteroid_speed)

            if collide(powerup, player):
                if powerup.type == "health" :
                    lives += 1
                elif powerup.type == "noCollideDamage":
                    effect_timer_start = pygame.time.get_ticks()
                    player.sheild()
                    damage = 0
                else:
                    powerup.effect()
                    effect_timer_start = pygame.time.get_ticks()

                mixer.Sound('sounds/lifeadd.ogg').play()
                powerups.remove(powerup)
                player.score += 3
            elif powerup.y + powerup.get_height()> HEIGHT :
                powerups.remove(powerup)
            # if pygame.time.get_ticks() - effect_timer_start >= effect_time_limit:
            #     Ship.COOLDOWN = 40
        # making powerup effect timer
        if effect_timer_start != None:
            if pygame.time.get_ticks() - effect_timer_start >= effect_time_limit:
                Ship.COOLDOWN = 40
                damage = 1
                player.ship_img = PLAYER_SPACE_SHIP
        #shooting player lasers as checking if we hit enemies or asteroids
        player.move_lasers(-laser_vel,enemies)
        player.move_lasers(-laser_vel,asteroids)

# Making the option interface where player controls background music
def options():
    run = True
    #making function to get font of with specefic size
    def menu_font(size) :
         return pygame.font.SysFont("comicsans", size)
    while run:
        WIN.blit(BG, (0, 0))
        MENU_MOUSE_POS = pygame.mouse.get_pos()
        #Displaying text
        SOUND_MENU_TEXT = menu_font(20).render("Background Music Control", True, "#b68f40")
        SOUND_MENU_RECT = SOUND_MENU_TEXT.get_rect(center=(200, 120))
        # Displaying buttons
        SOUND_PLAY_BUTTON = Button(image=pygame.transform.scale(pygame.image.load("assets/sound_on.png"),(50,50)).convert_alpha(), pos=(WIDTH/2+20, 120),
                             text_input="", font=menu_font(60), base_color="#d7fcd4", hovering_color="White")
        SOUND_MUTE_BUTTON = Button(image=pygame.transform.scale(pygame.image.load("assets/sound_off.png"),(50,50)).convert_alpha(), pos=(WIDTH/2+150, 120),
                                text_input="", font=menu_font(50), base_color="#d7fcd4", hovering_color="White")
        BACK_BUTTON = Button(image=pygame.image.load("assets/Button.png"), pos=(WIDTH/2, 570),
                             text_input="BACK", font=menu_font(50), base_color="#d7fcd4", hovering_color="White")

        WIN.blit(SOUND_MENU_TEXT, SOUND_MENU_RECT)

        for button in [SOUND_PLAY_BUTTON, SOUND_MUTE_BUTTON, BACK_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(WIN)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            # adding funcionality to buttons and adding sound effect to back button
            if event.type == pygame.MOUSEBUTTONDOWN:
                if SOUND_PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    mixer.Sound('sounds/select-sound.ogg').play()
                    mixer.music.play()
                if SOUND_MUTE_BUTTON.checkForInput(MENU_MOUSE_POS):
                    mixer.Sound('sounds/select-sound.ogg').play()
                    mixer.music.pause()
                if BACK_BUTTON.checkForInput(MENU_MOUSE_POS):
                    mixer.Sound('sounds/select-sound.ogg').play()
                    run = False
# Making main menu screen and implementing functionality
def main_menu():
    # making player name variable from string returned by name page which is player name
    player_name = name_page()

    run = True
    # function to get font of specific size
    def menu_font(size) :
         return pygame.font.SysFont("comicsans", size)
    while run:
        WIN.blit(BG, (0, 0))
        #adding text
        MENU_MOUSE_POS = pygame.mouse.get_pos()
        MENU_TEXT = menu_font(70).render("MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(WIDTH/2, 120))
        # adding buttons
        PLAY_BUTTON = Button(image=pygame.image.load("assets/Button.png"), pos=(WIDTH/2, 270),
                             text_input="PLAY", font=menu_font(60), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("assets/Button.png"), pos=(WIDTH/2, 420),
                                text_input="OPTIONS", font=menu_font(50), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Button.png"), pos=(WIDTH/2, 570),
                             text_input="QUIT", font=menu_font(50), base_color="#d7fcd4", hovering_color="White")

        WIN.blit(MENU_TEXT, MENU_RECT)
        # adding functionality to buttons and add sound effects
        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(WIN)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    mixer.Sound('sounds/select-sound.ogg').play()
                    main(player_name)


                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    mixer.Sound('sounds/select-sound.ogg').play()
                    options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    run = False
                    pygame.quit()



def ranking_page():
    # Read scores from file
    pageTime = 5000  # Spawn a power-up every 5 seconds (adjust as needed)
    pageTimerStart= pygame.time.get_ticks()
    run = True
    def menu_font(size) :
         return pygame.font.SysFont("comicsans", size)
    #
    if not os.path.exists("scores.json"):
        with open("scores.json", "w") as f:
            f.write("{}")

    with open("scores.json", "r") as f:
        scores = json.load(f)

    # Sort scores in decending order
    sorted_scores = sorted(scores.items(), key=lambda x: x[1],reverse=True)
    print(sorted_scores)
    print(scores.items())
    top_scores = sorted_scores[:10]  # Get top ten scores
    WIN.blit(BG,(0,0))
    RANKING_TEXT = menu_font(70).render("Top Rankings are ", True, "#b68f40")
    RANKING_RECT = RANKING_TEXT.get_rect(center=(WIDTH / 2, 120))
    # WIN.blit(RANKING_TEXT)
#Setting timer to make ranking page disappear after pageTime
    while run:
        if pygame.time.get_ticks() - pageTimerStart >= pageTime:
            run = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                return

        WIN.blit(BG,(0,0))
        # adding text
        WIN.blit(RANKING_TEXT,RANKING_RECT)
        text_y = RANKING_RECT.bottom+45

        # Display top ten scores
        # Displaying scores from file
        for i, (player_name, score) in enumerate(top_scores):
            text = f"{i+1}. {player_name}: {score}"
            text_render = menu_font(30).render(text, True, (255,255,255))
            WIN.blit(text_render, (100, text_y))
            text_y += 35

        pygame.display.update()

# Making a page to add username for rankings
def name_page():

    name_page_background = pygame.transform.scale(pygame.image.load("assets/bg2.jpg"),(750,750)).convert_alpha()

    run = True
    screen = pygame.display.set_mode((name_page_background.get_width(), name_page_background.get_height()))

    font = pygame.font.Font(None, 36)
    #Making input box to get input from user
    input_box_width = 300
    input_box_height = 40
    input_box_x = (WIDTH - input_box_width) // 2
    input_box_y = ((HEIGHT - input_box_height) // 2)+170
    input_box = pygame.Rect(input_box_x, input_box_y, input_box_width, input_box_height)
    # setting base color  and hovering color
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    user_text = ''
    placeholder_text = 'Enter your name'

    active = False
    # Checking events and assign text user write to a variable
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                    if active:
                        user_text = ''
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return user_text
                    elif event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    else:
                        line_width = font.size(user_text + event.unicode)[0]
                        if line_width <= input_box_width:
                            user_text += event.unicode
        screen.blit(name_page_background,(0,0))
        pygame.draw.line(screen, color, (input_box.x, input_box.y + input_box.height),
                         (input_box.x + input_box.width, input_box.y + input_box.height), 2)
        if not active and user_text == '':
            text_surface = font.render(placeholder_text, True, pygame.Color('gray'))
            screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))
        else:
            text_surface = font.render(user_text, True, (255,255,255))
            screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))
        pygame.display.update()

mixer.music.load('sounds/bgm.ogg')
mixer.music.play(-1)

main_menu()


