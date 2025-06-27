import pygame
from os.path import join
from os import walk
from random import choice, random, choices, randint

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

BLOCK_SIZE = 128
PLAYER_SIZE = 32

LEVEL_TYPE = 1
# LEVEL_TYPE = 3

QUERY_PARAMS = {    
    # 'WIDTH' : randint(20, 40),
    # 'HEIGHT' : randint(20, 40),
    'WIDTH' : 25,
    'HEIGHT' : 25,
    
    'SEED' : randint(0, 10000),
    'SCALE' : random() * 4.0,
    'MIN_LEAF_SIZE' : randint(1, 8),
    'MAX_LEAF_SIZE' : randint(8, 15),
    'WALL_PROBABILITY' : random(),
    'THRESHOLD' : random() * 5,
    'MIN_ROOM_SIZE' : randint(0, 3),
    'MAX_ROOMS' : randint(3, 8),
    'ITERATIONS' : randint(1, 5)
}

# Constants
BASE_WIDTH = 30
BASE_HEIGHT = 30
BASE_JUMP = 12
BASE_PLAYER_SPEED = 600
PLAYER_GRAVITY = 10

# Scaling factors (tune for balance)
JUMP = BASE_JUMP * (QUERY_PARAMS["HEIGHT"] / BASE_HEIGHT)
PLAYER_SPEED = BASE_PLAYER_SPEED * (QUERY_PARAMS["WIDTH"] / BASE_WIDTH)

JUMP = round(JUMP)
PLAYER_SPEED = round(PLAYER_SPEED)
print("---------------")
print("Jump Height:", JUMP)
print("Player Speed:", PLAYER_SPEED)

BLOCKS = {
    1: {'color':choice(['light green','antiquewhite', 'brown4', 'cadetblue3']), 'name':'floor'},
    2: {'color':choice(['black', 'cornflowerblue', 'cornsilk2', 'darkolivegreen', 'gray28']), 'name':'wall'},
    3: {'color':'blue', 'name':'water'}
}
