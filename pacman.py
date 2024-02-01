import pygame

pygame.init()

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 950
FPS = 60

screen = pygame.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])
timer = pygame.time.Clock()
font = pygame.font.Font("freesansbold.ttf", 20)
