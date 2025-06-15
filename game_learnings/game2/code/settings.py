import pygame
from os.path import join

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
SIZE = {
    'paddle': (40,100),
    'ball': (30,30)
}
SPEED={
    'player': 500,
    'opponent': 250,
    'ball': 450
}
POS = {
    'player': (WINDOW_WIDTH-50, WINDOW_HEIGHT/2),
    'oppenent': (50, WINDOW_HEIGHT/2)
}
COLORS = {
    'paddle':'#ee322c',
    'paddle_shadow':'#b12521',
    'ball':'#ee622c',
    'ball_shadow':'#c14f24',
    'bg':'#002633'
}