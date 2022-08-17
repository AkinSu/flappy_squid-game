import random
from time import time
from pygame.locals import *
import pygame
from pygame import mixer

pygame.init()

Charecter = random.randint(0,1)
clock = pygame.time.Clock()
fps = 60

screen_width = 860
screen_height = 700

display = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Squid')

#font
font = pygame.font.SysFont('assets/font/KrabbyPatty-PKZAB.ttf', 60)
white =(255, 255, 255)

# define game variables
floor_scroll = 0
scroll_speed = 7
is_jumping = False
flying = False
game_over = False
pipe_gap = 170
pipe_freq = 1000 #milli secs 
last_pipe = pygame.time.get_ticks() - pipe_freq
score = 0
pass_pipe = False
step_count = 1


# background images
bg_image = pygame.image.load('assets/BG.png')
bg_image_floor = pygame.image.load('assets/BG_floor.png')
button_image = pygame.image.load('assets/restart.png')

# sounds
death_sfx = pygame.mixer.Sound('assets/Spongebob_Fail_Sound.mp3')

# collision detection
# def collision_detection (pipe_x, pipe_height, bitd_y, bottom_pipe_height):
#     if pipe_x >= 

def reset_game():
    scroll_speed = 7
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    gameq_over = False
    flying = False 
    is_jumping = False
    #Bird.image = pygame.transform.rotate(0,0)
    score = 0
    return score


def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    display.blit(img, (x, y))

class Bird(pygame.sprite.Sprite):
    def __init__(self, x,  y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for nums in range(1, 4):
            if Charecter == 1:
                img = pygame.image.load(f'assets/UGbird{nums}.png')
            elif Charecter == 0:
                img = pygame.image.load(f'assets/bird{nums}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect =self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):

        if flying == True:
        
            self.vel += 0.5
            if self.vel > 12:
                self.vel = 12
            if self.rect.bottom < 660:
                self.rect.y += int(self.vel)
        if game_over == False:
            # jump
            if is_jumping == True and self.clicked == False:
                flap_sfx.play() 
                self.clicked = True
                self.vel = -10        
            if is_jumping == False:
                self.clicked = False

            self.counter += 1
            flap_cooldown = 5
            
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]
            
            #rotate
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -1.8)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -70)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/pipe.png')
        self.rect = self.image.get_rect()
        if pos == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if pos == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):

        action = False

        pos = pygame.mouse.get_pos()
        # check if mouse is ever the button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] ==1:
                action = True

        display.blit(self.image, (self.rect.x, self.rect.y))

        return action

bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))

bird_group.add(flappy)
button = Button(screen_width / 2 - 100, screen_height / 2 - 80, button_image)

#pygame.display.update()

running = True
while running:

    clock.tick(fps)

    display.fill((0, 0, 0))

    display.blit(bg_image, (0, 0))
    # flapping sound
    if(is_jumping):
        step_count += 1
        if step_count > 2:
            step_count = 1
    flap_sfx = pygame.mixer.Sound(f'assets/step{step_count}.mp3')
    bird_group.draw(display)
    bird_group.update()
    pipe_group.draw(display)

    
    scroll_speed += score * 0.0009

    # draw ground
    display.blit(bg_image_floor, (floor_scroll, 0))

    #check the score
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
            and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0] .rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False
    draw_text(str(score), font , white, int(screen_width / 2) - 10, 20)

    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True

    # check if bird hits the ground
    if flappy.rect.bottom >= 660:
        game_over = True
        flying = False

    if game_over == False and flying == True:
        # generate new pipe
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_freq:
            pipe_height = random.randint(-130, 130)
            bottom_pipe = Pipe(screen_width, int(screen_height / 2.3) + pipe_height,  -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2.3) + pipe_height, 1)
            pipe_group.add(bottom_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        floor_scroll -= scroll_speed
        if abs(floor_scroll) > 30:
            floor_scroll = 0
        pipe_group.update()


    # check for game over then reset
    if game_over == True:
        if button.draw() == True:
            game_over == False
            score = reset_game()
    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYUP:
            is_jumping = False
        if event.type == pygame.KEYDOWN:
            is_jumping = True

        if event.type == pygame.KEYUP and flying == False and game_over == False:
            flying = True
           
    pygame.display.update()

# Quit the program 
pygame.quit()
quit()