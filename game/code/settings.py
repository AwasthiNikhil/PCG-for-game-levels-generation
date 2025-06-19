import pygame
from os.path import join

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

BLOCK_SIZE = 128
PLAYER_SIZE = 32

BLOCKS = {
    1: {'color':'light green', 'name':'floor'},
    2: {'color':'black', 'name':'wall'},
    3: {'color':'blue', 'name':'water'}
}

