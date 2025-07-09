# settings.py
from random import choice
# WIDTH = 1920
# HEIGHT = 1080
WIDTH = 1280
HEIGHT = 720
FPS = 60
TITLE = "Lucky You"

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 150, 255)
GRAY = (200, 200, 200)
BLOCK_SIZE = 128
BLOCKS = {
    1: {'color':choice(['light green','antiquewhite', 'brown4', 'cadetblue3']), 'name':'floor'},
    2: {'color':choice(['black', 'cornflowerblue', 'cornsilk2', 'darkolivegreen', 'gray28']), 'name':'wall'},
    3: {'color':'blue', 'name':'water'}
}
