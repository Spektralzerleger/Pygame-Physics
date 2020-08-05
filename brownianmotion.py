"""Editor: Eugen Dizer
Last modified: 01.08.2020

This is a simulation of the Brownian motion. A lot of small particles are flying around and behaving like
an ideal gas. The big particle is influenced by all the other particles and moves around randomly.

To Do: Track position, add buttons for adjusting parameters, ..., get animation smooth!!!...
"""

import pygame, sys
import numpy as np
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (40, 80)

# Default radius and mass of the big ball
R = 20
M = 20

# Default radii and masses of the small balls
r = 2
m = 1

# Default number of balls
N = 200  ### Problem with many balls

# Gravity (maybe for a gas in a box simulation???)
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
        #self.vy += g * t
        self.x += self.vx * t
        self.y += self.vy * t    

        self.screen_collision()

    def screen_collision(self):
        # Collision with the left screen side
        if self.x - self.radius <= 0:
            self.x = 0 + self.radius
            self.vx *= - 1
            #self.vx *= elasticity
        # Collision with the right screen side
        if self.x + self.radius >= screen_width:
            self.x = screen_width - self.radius
            self.vx *= - 1
            #self.vx *= elasticity
        # Collision with the top of the screen
        if (self.y - self.radius <= 0) and (self.vy <= 0):
            self.y = 0 + self.radius
            self.vy *= - 1
            #self.vy *= elasticity
        # Collision with the bottom of the screen
        if (self.y + self.radius >= screen_height) and (self.vy >= 0):
            self.y = screen_height - self.radius
            self.vy *= - 1
            #self.vy *= elasticity

    def ball_collision(self, otherBall, t):
        # Distance between the two ball centers
        d = np.sqrt((self.x - otherBall.x) ** 2 + (self.y - otherBall.y) ** 2)

        if d <= self.radius + otherBall.radius:
            # Parameters of the first ball
            m1 = self.mass
            x1 = self.x; v1x = self.vx
            y1 = self.y; v1y = self.vy
            # Parameters of the second ball
            m2 = otherBall.mass
            x2 = otherBall.x; v2x = otherBall.vx
            y2 = otherBall.y; v2y = otherBall.vy
            # -cos() and sin()
            d_0x = (x1 - x2) / np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            d_0y = (y1 - y2) / np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            # Factor
            k = (2 * (d_0x * (v2x - v1x) + d_0y * (v2y - v1y))) / (1 / m1 + 1 / m2)

            # Elasticity
            friction = 0.95  # could do it as global parameter
            v1x_prime = v1x + (k / m1) * d_0x
            v1y_prime = v1y + (k / m1) * d_0y
            v2x_prime = v2x - (k / m2) * d_0x
            v2y_prime = v2y - (k / m2) * d_0y
            
            # Set new position, such that the balls aren't inside each other anymore
            delta = self.radius + otherBall.radius - d
            self.x += delta * d_0x
            self.y += delta * d_0y

            # Set new velocities
            self.vx = v1x_prime * friction
            otherBall.vx = v2x_prime * friction
            self.vy = v1y_prime * friction
            otherBall.vy = v2y_prime * friction

            #self.move(t)
            #otherBall.move(t)


def textObject(text, font, color):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()

def draw_text(x, y, length, height, font, message, color):
    textSurface, textRect = textObject(message, font, color)
    textRect.center = ((x + length / 2)), ((y + height / 2))
    screen.blit(textSurface, textRect)

def start_button(x, y, length, height, color_normal, color_active, text_color): ### Could make also class with start and restart function...
    global start
    if (mouse[0] > x) and (mouse[0] < x + length) and (mouse[1] > y) and (mouse[1] < y + height):
        pygame.draw.rect(screen, color_active, (x, y, length, height))
        if click[0] == 1:
            start = True
            # Make it wait for some time to not collide with the start button
            pygame.time.delay(400)
    else:
        pygame.draw.rect(screen, color_normal, (x, y, length, height))

    draw_text(x, y, length, height, font, "Start", text_color)

def restart_button(x, y, length, height, color_normal, color_active, text_color):
    global start, balls
    if (mouse[0] > x) and (mouse[0] < x + length) and (mouse[1] > y) and (mouse[1] < y + height):
        pygame.draw.rect(screen, color_active, (x, y, length, height))
        if click[0] == 1:
            start = False
            balls = init_balls() ########## FIX!!!
            # Make it wait for some time to not collide with the start button
            pygame.time.delay(400)
    else:
        pygame.draw.rect(screen, color_normal, (x, y, length, height))

    draw_text(x, y, length, height, font, "Restart", text_color)


class Input:
    def __init__(self, x, y, length, height, color_normal, color_active, func):
        self.x = x
        self.y = y
        self.length = length
        self.height = height
        self.color_normal = color_normal
        self.color_active = color_active
        self.func = func

        self.active = False

        # Initial entries in input boxes
        if self.func == "N":
            self.input = str(N)
        elif self.func == "g":
            self.input = str(g / 100)
        elif self.func == "e":
            self.input = str(elasticity)
        else:
            self.input = "1"

    def draw_input_box(self):
        if (mouse[0] > self.x) and (mouse[0] < self.x + self.length) and (mouse[1] > self.y) and (mouse[1] < self.y + self.height):
            pygame.draw.rect(screen, self.color_active, (self.x, self.y, self.length, self.height), 2)
            if click[0] == 1:
                self.active = True
        elif self.active == True:
            pygame.draw.rect(screen, self.color_active, (self.x, self.y, self.length, self.height), 2)
            if click[0] == 1:
                self.active = False
        else:
            pygame.draw.rect(screen, self.color_normal, (self.x, self.y, self.length, self.height), 2)

        draw_text(self.x, self.y, self.length, self.height, font, self.input, self.color_normal) ### Display input

        ### Functionality
        if self.func == "N":
            global N, r, m, balls, Inputs   ### FIX input functions
            draw_text(self.x - 65, self.y + 5, self.length + 20, self.height - 10, font, self.func + " = ", WHITE) # Could adjust text size

            if len(self.input) == 1:
                N = int(self.input)                        ### FIX ball initialization, call function
                r = list((5*np.ones(N)).astype(np.uint8))
                m = list(np.ones(N).astype(np.uint8))
                balls = init_balls()
                #Inputs = init_inputs()

        elif self.func == "g":
            global g
            draw_text(self.x - 65, self.y + 5, self.length + 20, self.height - 10, font, self.func + " = ", WHITE) # Could adjust text size

            if len(self.input) > 0:
                g = 100 * float(self.input)

        elif self.func == "e":
            global elasticity
            draw_text(self.x - 65, self.y + 5, self.length + 20, self.height - 10, font, self.func + " = ", WHITE) # Could adjust text size

            if len(self.input) > 0:
                elasticity = float(self.input)
        
        elif self.func[0] == "m":
            #global m
            draw_text(self.x - 65, self.y + 5, self.length + 20, self.height - 10, font, self.func + " = ", WHITE) # Could adjust text size
            
            if len(self.input) > 0:
                # Assumption: ball numbers are from 1 to 9
                m[int(self.func[1]) - 1] = float(self.input)
                pass
            ##### FIX!! mass setting! and radius with mass...

        else:
            draw_text(self.x - 65, self.y + 5, self.length + 20, self.height - 10, font, self.func + " = ", WHITE)



# Initialize pygame window
pygame.init()
screen_width = 800
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

# Initialize balls
initial_height = 250

def init_balls():
    balls = []
    balls.append(Ball(250, initial_height, 0, 0, R, M, WHITE)) # Big ball
    for i in range(N):
        balls.append(Ball(np.random.randint(screen_width), np.random.randint(screen_height), 100 - np.random.randint(250), 100 - np.random.randint(250), r, m, WHITE)) # Small balls, set random position
        # np.random e.g.

    return balls

balls = init_balls()

# Initialize input boxes
def init_inputs():
    Inputs = []
    N_Input = Input(65, 100, 60, 30, WHITE, RED, "N")
    g_Input = Input(236, 100, 60, 30, WHITE, RED, "g")
    e_Input = Input(410, 100, 60, 30, WHITE, RED, "e")
    Inputs.append(N_Input)
    Inputs.append(g_Input)
    Inputs.append(e_Input)

    return Inputs

Inputs = init_inputs()


start = False
finished = False

# Game loop
while True:
    pygame.event.pump()
    fps = clock.tick(FPS) / 1000
    dt = clock.get_time() / 1000  ### FIX time.... make animation smooth!! Maybe use sprites? rects...
    #print(dt)

    # Handling input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            # Loop over all input boxes
            for i in range(len(Inputs)):
                if Inputs[i].active == True:
                    if event.key == pygame.K_BACKSPACE:
                        Inputs[i].input = Inputs[i].input[:-1]
                    else:
                        if len(Inputs[i].input) < 4:  ### For N_Input??? FIX INPUT...
                            Inputs[i].input += event.unicode
                            Inputs[i].active = False

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # Visuals
    screen.fill(bg_color)

    if start == False:
        # FIX buttons
        start_button(200, 20, 100, 50, WHITE, RED, BLACK)
        for i in range(len(Inputs)):
            Inputs[i].draw_input_box()
        for j in range(N + 1):
            balls[j].draw()
    elif start == True: # or elif
        restart_button(200, 20, 100, 50, WHITE, RED, BLACK)
        for i in range(N + 1):
            balls[i].draw()
            balls[i].move(dt)
        for i in range(N):
            for j in range(i + 1, N + 1):
                balls[i].ball_collision(balls[j], dt)

    pygame.display.flip()