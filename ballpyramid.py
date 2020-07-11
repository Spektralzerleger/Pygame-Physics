"""Editor: Eugen Dizer
Last modified: 11.07.2020


This is a template code for pygame...
Draw your things here and implement the physics! 
In the end, I want to have a program with a lot of physics simulation tools.

Ideas:
    * Ball Pyramid
    * Ray deflection
    * ...


This is the so called ball pyramid or super jump, also known as Galilean cannon:
Some balls are stacked and released from a height h. When they arrive at the ground, they are
reflected and the smallest ball on the top is fired out to a very large height.
Implement the balls, some graphics and the physics of the collision:
https://de.wikipedia.org/wiki/Doppelball-Versuch

To Do: Add buttons on the screen: start, stop, play speed (tune gravity parameter), number of balls...
        max height, theoretical max height, ...
"""

import pygame, sys
import numpy as np
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (40, 80)

# Default radii and masses of the balls
r = [5, 10, 15]
m = [1, 1.2, 1.5]

# Default number of balls
N = len(r)

# Gravity / Speed
g = 981

# Elasticity
elasticity = 0.9


class Ball:
    def __init__(self, x, y, vx, vy, radius, mass, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.mass = mass
        self.color = color

    def draw(self):
        pygame.draw.circle(screen, self.color, (round(self.x), round(self.y)), self.radius)

    def move(self, t):
        # Gravity
        self.vy += g * t
        self.y += self.vy * t    

        self.screen_collision()

    def screen_collision(self):
        # Collision with the left screen side
        if self.x - self.radius <= 0:
            self.x = 0 + self.radius
            self.vx *= - 1
        # Collision with the right screen side
        if self.x + self.radius >= screen_width:
            self.x = screen_width - self.radius
            self.vx *= - 1
        # Collision with the top of the screen
        if (self.y - self.radius <= 0) and (self.vy <= 0):
            pass
        # Collision with the bottom of the screen
        if (self.y + self.radius >= screen_height) and (self.vy >= 0):
            self.y = screen_height - self.radius
            self.vy *= - 1
            self.vy *= elasticity
        # Stop the ball when it's resting on the ground, FIX!!!
        if (self.vy == 0) and (self.y + self.radius - screen_height == screen_height):
            self.vy = 0 ## FIX

    def ball_collision(self, otherBall, t):
        if np.sqrt((self.x - otherBall.x) ** 2 + (self.y - otherBall.y) ** 2) <= self.radius + otherBall.radius:
            if (self.vy >= 0 and otherBall.vy <= 0) or (self.vy <= 0 and otherBall.vy <= 0 and abs(self.vy) < abs(otherBall.vy)) or (self.vy >= 0 and otherBall.vy >= 0 and self.vy > otherBall.vy):
                self.y = otherBall.y - (self.radius + otherBall.radius)
                vy = self.vy
                self.vy = (2 * otherBall.mass * otherBall.vy + (self.mass - otherBall.mass) * self.vy) / (self.mass + otherBall.mass)
                otherBall.vy = (2 * self.mass * vy + (otherBall.mass - self.mass) * otherBall.vy) / (self.mass + otherBall.mass)
                self.vy *= elasticity
                otherBall.vy *= elasticity


def textObject(text, font, color):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()

def draw_text(x, y, length, height, font, message, color):
    textSurface, textRect = textObject(message, font, color)
    textRect.center = ((x + length / 2)), ((y + height / 2))
    screen.blit(textSurface, textRect)

def start_button(x, y, length, height, color_normal, color_active, text_color): ### Could make also class with start and restart function...
    global countdown, start_ticks
    if (mouse[0] > x) and (mouse[0] < x + length) and (mouse[1] > y) and (mouse[1] < y + height):
        pygame.draw.rect(screen, color_active, (x, y, length, height))
        if click[0] == 1:
            if countdown == False:
                start_ticks = pygame.time.get_ticks()
                countdown = True
    else:
        pygame.draw.rect(screen, color_normal, (x, y, length, height))

    draw_text(x, y, length, height, font, "Start", text_color)

def restart_button(x, y, length, height, color_normal, color_active, text_color):
    global balls
    if (mouse[0] > x) and (mouse[0] < x + length) and (mouse[1] > y) and (mouse[1] < y + height):
        pygame.draw.rect(screen, color_active, (x, y, length, height))
        if click[0] == 1:
            for i in range(N):
                balls[i] = InitialBalls[i]    ################ FIX!!!
    else:
        pygame.draw.rect(screen, color_normal, (x, y, length, height))

    draw_text(x, y, length, height, font, "Restart", text_color)

def count_down(x, y, font, color):
    global countdown, start
    if countdown == True:
        seconds = (pygame.time.get_ticks() - start_ticks) / 1000
        if int(seconds) < 3:
            draw_text(x, y, 50, 50, font, str(3-int(seconds)), color)
        else:
            countdown = False
            start = True

def input_box(x, y, length, height, color_normal, color_active, text):    ######## Make a class from this!
    global active, N
    if (mouse[0] > x) and (mouse[0] < x + length) and (mouse[1] > y) and (mouse[1] < y + height):
        pygame.draw.rect(screen, color_active, (x, y, length, height), 2)
        if click[0] == 1:
            active = True
    elif active == True:
        pygame.draw.rect(screen, color_active, (x, y, length, height), 2)
        if click[0] == 1:
            active = False
    else:
        pygame.draw.rect(screen, color_normal, (x, y, length, height), 2)

    draw_text(x, y, length, height, font, text, color_normal)
    
    if len(text) == 1:
        N = int(text)   ### FIX ball initialization



# Initialize pygame window
pygame.init()
screen_width = 500
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Ball Pyramid")
font = pygame.font.SysFont("Comic Sans MS", 20)

clock = pygame.time.Clock()
FPS = 200  # This variable will define how many frames we update per second.

# Some colors
bg_color = pygame.Color("grey12")
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Initialize balls, generalize
balls = []
balls.append(Ball(250, 250, 0, 0, r[0], m[0], WHITE))
radius = r[0]
for i in range(N - 1):
    balls.append(Ball(250, 250 + (radius + r[i+1]), 0, 0, r[i + 1], m[i + 1], WHITE))
    radius += 2 * r[i+1] + 2

# Make a copy for restart function, FIX!!!
InitialBalls = balls

text = ""
active = False
countdown = False
start = False
finished = False

# Game loop
while True:
    pygame.event.pump()
    dt = clock.tick(FPS) / 1000

    # Handling input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if active == True:
                if event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    if len(text) < 1:
                        text += event.unicode
                        active = False

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # Visuals
    screen.fill(bg_color)

    if (start == False) and (countdown == False):
        for i in range(N):
            balls[i].draw()
            start_button(200, 20, 100, 50, WHITE, RED, BLACK)
            draw_text(0, 80, 80, 40, font, "N =", WHITE) # Combine these two
            input_box(65, 86, 60, 30, WHITE, RED, text)
    if (start == False) and (countdown == True):
        for i in range(N):
            balls[i].draw()
            count_down(226, 20, font, RED)
    if start == True:
        restart_button(200, 20, 100, 50, WHITE, RED, BLACK)
        for i in range(N):
            balls[i].draw()
            balls[i].move(dt)
        for i in range(N - 1):
            balls[i].ball_collision(balls[i + 1], dt)
    if finished == True:  # FIX: When it's finished?
        for i in range(N):
            balls[i].draw()
            restart_button(200, 20, 100, 50, WHITE, RED, BLACK)

    pygame.display.flip()