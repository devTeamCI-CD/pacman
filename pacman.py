import pygame
import copy
from board import boards
import math

pygame.init()

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 850
FPS = 60
MAZE_COLOR = 'blue'
DOT_COLOR = 'orange'

screen = pygame.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])
timer = pygame.time.Clock()
font = pygame.font.Font("freesansbold.ttf", 20)
level = copy.deepcopy(boards)
flicker = False

def draw_board():
    num1 = ((WINDOW_HEIGHT - 50) // 32)
    num2 = (WINDOW_WIDTH // 30)
    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] == 1:
                pygame.draw.circle(screen, DOT_COLOR, (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 4)
            if level[i][j] == 2 and not flicker:
                pygame.draw.circle(screen, DOT_COLOR, (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 10)
            if level[i][j] == 3:
                pygame.draw.line(screen, MAZE_COLOR, (j * num2 + (0.5 * num2), i * num1),
                                 (j * num2 + (0.5 * num2), i * num1 + num1), 3)
            if level[i][j] == 4:
                pygame.draw.line(screen, MAZE_COLOR, (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)
            if level[i][j] == 5:
                pygame.draw.arc(screen, MAZE_COLOR, [(j * num2 - (num2 * 0.4)) - 2, (i * num1 + (0.5 * num1)), num2, num1],
                                0, math.pi / 2, 3)
            if level[i][j] == 6:
                pygame.draw.arc(screen, MAZE_COLOR,
                                [(j * num2 + (num2 * 0.5)), (i * num1 + (0.5 * num1)), num2, num1], math.pi / 2, math.pi, 3)
            if level[i][j] == 7:
                pygame.draw.arc(screen, MAZE_COLOR, [(j * num2 + (num2 * 0.5)), (i * num1 - (0.4 * num1)), num2, num1], math.pi,
                                3 * math.pi / 2, 3)
            if level[i][j] == 8:
                pygame.draw.arc(screen, MAZE_COLOR,[(j * num2 - (num2 * 0.4)) - 2, (i * num1 - (0.4 * num1)), num2, num1], 3 * math.pi / 2,
                                2 * math.pi, 3)
            if level[i][j] == 9:
                pygame.draw.line(screen, DOT_COLOR, (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)



run = True
while run:
    timer.tick(FPS)
    screen.fill('black')
    draw_board()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.flip()
pygame.quit()