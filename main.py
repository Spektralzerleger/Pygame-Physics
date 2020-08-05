"""Editor: Eugen Dizer
Last modified: 05.08.2020


This is a template code for pygame...
Draw your things here and implement the physics! 
In the end, I want to have a program with a lot of physics simulation tools.

Ideas:
    * Ball Pyramid
    * Brownian Motion
    * Ray deflection
    * ...

"""

import pygame, sys
import numpy as np
import os

os.environ["SDL_VIDEO_WINDOW_POS"] = "%d,%d" % (40, 40)


### Shift this to another file and then include!
##########################################################################################
def textObject(text, font, color):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()

def draw_text(x, y, length, height, font, message, color):
    textSurface, textRect = textObject(message, font, color)
    textRect.center = ((x + length / 2)), ((y + height / 2))
    screen.blit(textSurface, textRect)

def start_button(x, y, length, height, color_normal, color_active, text_color):
    if (mouse[0] > x) and (mouse[0] < x + length) and (mouse[1] > y) and (mouse[1] < y + height):
        pygame.draw.rect(screen, color_active, (x, y, length, height))
        if click[0] == 1:
            import ballpyramid
    else:
        pygame.draw.rect(screen, color_normal, (x, y, length, height))

    draw_text(x, y, length, height, font, "Start", text_color)
#########################################################################################


# Initialize pygame window
pygame.init()
screen_width = 900
screen_height = 675
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pygame Physics Simulation Tool")
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

# Background image
background = pygame.image.load('background.jpg')


# Game loop
while True:
    pygame.event.pump()
    dt = clock.tick(FPS) / 1000

    # Handling input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # Visuals
    screen.fill(bg_color)
    # Background image
    screen.blit(background, (0, 0))
    
    # Find a way how to include other programs like ballpyramid.py
    # E.g. if mouse click, then import ballpyramid
    start_button(400, 40, 100, 50, WHITE, RED, BLACK)
    # Find a way to exit into main loop again...
    # E.g. change exit function of input files...
    # If you click on exit then close the inner loop and not the whole game!
    

    pygame.display.flip()