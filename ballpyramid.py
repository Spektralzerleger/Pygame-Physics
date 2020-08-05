"""Editor: Eugen Dizer
Last modified: 05.08.2020

This is the so called ball pyramid or super jump, also known as Galilean cannon:
Some balls are stacked and released from a height h. When they arrive at the ground, they are
reflected and the smallest ball on the top is fired out to a very large height.
Implement the balls, some graphics and the physics of the collision:
https://de.wikipedia.org/wiki/Doppelball-Versuch

To Do: Fix bugs, add information, theoretical max height for 2 or 3 balls, add collision sound...
"""

import pygame, sys
import numpy as np
import os

os.environ["SDL_VIDEO_WINDOW_POS"] = "%d,%d" % (40, 80)

# Default radii and masses of the balls
r = [5, 7, 10]
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
            self.vx *= -1
        # Collision with the right screen side
        if self.x + self.radius >= screen_width:
            self.x = screen_width - self.radius
            self.vx *= -1
        # Collision with the top of the screen
        if (self.y - self.radius <= 0) and (self.vy <= 0):
            pass
        # Collision with the bottom of the screen
        if (self.y + self.radius >= screen_height) and (self.vy >= 0):
            self.y = screen_height - self.radius
            self.vy *= -1
            self.vy *= elasticity
        # Stop the ball when it's resting on the ground, FIX!!! Do I need it?
        if (self.vy == 0) and (self.y + self.radius - screen_height == screen_height):
            self.vy = 0  ## FIX

    def ball_collision(self, otherBall, t):
        if np.sqrt((self.x - otherBall.x) ** 2 + (self.y - otherBall.y) ** 2) <= self.radius + otherBall.radius:
            if (
                (self.vy >= 0 and otherBall.vy <= 0)
                or (self.vy <= 0 and otherBall.vy <= 0 and abs(self.vy) < abs(otherBall.vy))
                or (self.vy >= 0 and otherBall.vy >= 0 and self.vy > otherBall.vy)
            ):
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


def start_button(x, y, length, height, color_normal, color_active, text_color):  ### Could make also class with start and restart function...
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
    global start, countdown, balls, max_height
    if (mouse[0] > x) and (mouse[0] < x + length) and (mouse[1] > y) and (mouse[1] < y + height):
        pygame.draw.rect(screen, color_active, (x, y, length, height))
        if click[0] == 1:
            start = False
            countdown = False
            balls = init_balls()
            max_height = screen_height - initial_height
            # Make it wait for some time to not collide with the start button
            pygame.time.delay(400)
    else:
        pygame.draw.rect(screen, color_normal, (x, y, length, height))

    draw_text(x, y, length, height, font, "Restart", text_color)


def count_down(x, y, font, color):
    global countdown, start
    if countdown == True:
        seconds = (pygame.time.get_ticks() - start_ticks) / 1000
        if int(seconds) < 3:
            draw_text(x, y, 50, 50, font, str(3 - int(seconds)), color)
        else:
            countdown = False
            start = True


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
        elif self.func[0] == "m":
            self.input = str(m[int(self.func[1:]) - 1])

    def draw_input_box(self):
        if (mouse[0] > self.x) and (mouse[0] < self.x + self.length) and (mouse[1] > self.y) and (mouse[1] < self.y + self.height):
            pygame.draw.rect(screen, self.color_active, (self.x, self.y, self.length, self.height), 2)
            if click[0] == 1:
                self.active = True  # Activate button when you click on it
        elif self.active == True:
            pygame.draw.rect(screen, self.color_active, (self.x, self.y, self.length, self.height), 2)
            if click[0] == 1:
                self.active = False  # Deactivate button when you click somewhere else
        else:
            pygame.draw.rect(screen, self.color_normal, (self.x, self.y, self.length, self.height), 2)

        draw_text(self.x, self.y, self.length, self.height, font, self.input, self.color_normal)  ### Display input

        ### Functionality
        if self.func == "N":
            global N, r, m, balls, Inputs, I
            draw_text(self.x - 65, self.y + 5, self.length + 20, self.height - 10, font, self.func + " = ", WHITE)  # Could adjust text size

            if len(self.input) > 0:
                current_N = int(self.input)
                if current_N != N:
                    N = current_N
                    r = list((5 * np.ones(N)).astype(np.uint8))
                    m = list(np.ones(N).astype(np.uint8))
                    balls = init_balls()
                    Inputs = init_inputs()
                    I = len(Inputs)

        elif self.func == "g":
            global g
            draw_text(self.x - 65, self.y + 5, self.length + 20, self.height - 10, font, self.func + " = ", WHITE)  # Could adjust text size

            if len(self.input) > 0:
                g = 100 * float(self.input)

        elif self.func == "e":
            global elasticity
            draw_text(self.x - 65, self.y + 5, self.length + 20, self.height - 10, font, self.func + " = ", WHITE)  # Could adjust text size

            if len(self.input) > 0:
                elasticity = float(self.input)

        elif self.func[0] == "m":
            draw_text(self.x - 65, self.y + 5, self.length + 20, self.height - 10, font, self.func + " = ", WHITE)  # Could adjust text size

            if len(self.input) > 0:
                # Assumption: box name starts with m and is followed by mass number
                m[int(self.func[1:]) - 1] = float(self.input)
                if float(self.input) > 10:
                    r[int(self.func[1:]) - 1] = 5 * 10
                else:
                    r[int(self.func[1:]) - 1] = round(5 * float(self.input))
                balls = init_balls()

        else:
            draw_text(self.x - 65, self.y + 5, self.length + 20, self.height - 10, font, self.func + " = ", WHITE)


def draw_ball_height(x, y, length, height, color):
    global max_height
    current_height = int(screen_height - balls[0].y)
    draw_text(x - 40, y, length, height, font, "h = ", color)
    draw_text(x, y, length, height, font, str(screen_height - initial_height), color)  # Initial height
    if current_height > max_height:
        max_height = current_height
    draw_text(x - 40, y + 30, length, height, font, "H = ", color)
    draw_text(x, y + 30, length, height, font, str(max_height), color)  # Max height


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

# Initialize balls
initial_height = 250
max_height = screen_height - initial_height


def init_balls():
    balls = []
    balls.append(Ball(250, initial_height, 0, 0, r[0], m[0], WHITE))  # Top ball
    radius = r[0]
    # All the other balls
    for i in range(N - 1):
        balls.append(Ball(250, initial_height + (radius + r[i + 1]), 0, 0, r[i + 1], m[i + 1], WHITE))
        radius += 2 * r[i + 1]

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
    # Make N input boxes for m1, m2, ..., mN
    for i in range(N):
        Inputs.append(Input(65, 200 + 40 * i, 60, 30, WHITE, RED, "m{}".format(i + 1)))

    return Inputs


Inputs = init_inputs()
I = len(Inputs)

countdown = False
start = False

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
            # Loop over all input boxes
            for i in range(len(Inputs)):
                if Inputs[i].active == True:
                    if event.key == pygame.K_BACKSPACE:
                        Inputs[i].input = Inputs[i].input[:-1]
                    else:
                        if len(Inputs[i].input) < 4:
                            # Input should be integer or float
                            if event.unicode in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]:
                                Inputs[i].input += event.unicode
                            # Handling bad input
                            if (Inputs[i].input[0] == ".") or (Inputs[i].input.count(".") > 1):
                                Inputs[i].input = Inputs[i].input[:-1]
                        else:
                            Inputs[i].active = False

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # Visuals
    screen.fill(bg_color)

    if (start == False) and (countdown == False):
        start_button(200, 20, 100, 50, WHITE, RED, BLACK)
        for i in range(I):
            if i >= I:
                break
            Inputs[i].draw_input_box()
        for j in range(N):
            balls[j].draw()
    if (start == False) and (countdown == True):
        count_down(226, 20, font, RED)
        for i in range(N):
            balls[i].draw()
    if start == True:
        restart_button(200, 20, 100, 50, WHITE, RED, BLACK)
        draw_ball_height(100, 100, 30, 20, WHITE)
        for i in range(N):
            balls[i].draw()
            balls[i].move(dt)
        for i in range(N - 1):
            for j in range(i + 1, N):
                balls[i].ball_collision(balls[j], dt)

    pygame.display.flip()
