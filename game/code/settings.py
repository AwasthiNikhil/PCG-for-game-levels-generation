import pygame
from os.path import join
from os import walk

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

BLOCK_SIZE = 256
PLAYER_SIZE = 32

PLAYER = {
    'x': 600,
    'y': 900
}

BLOCKS = {
    1: {'color':'light green', 'name':'floor'},
    2: {'color':'black', 'name':'wall'},
    3: {'color':'blue', 'name':'water'}
}

