import pygame
import copy
from support.board import original_game_board

PLAYING_KEYS = {
    "up": [pygame.K_w, pygame.K_UP],
    "down": [pygame.K_s, pygame.K_DOWN],
    "right": [pygame.K_d, pygame.K_RIGHT],
    "left": [pygame.K_a, pygame.K_LEFT],
}

sprite_ratio = 3 / 2
game_board = copy.deepcopy(original_game_board)
square = 25  # Size of each unit square
sprite_offset = square * (1 - sprite_ratio) * (1 / 2)
(width, height) = (len(game_board[0]) * square, len(game_board) * square)  # Game screen
screen = pygame.display.set_mode((width, height))
music_playing = 0  # 0: Chomp, 1: Important, 2: Siren
pellet_color = (222, 161, 133)

ghostsafe_area = [15, 13]  # The location the ghosts escape to when attacked
ghost_gate = [[15, 13], [15, 14]]
