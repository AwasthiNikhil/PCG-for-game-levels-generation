import pygame
import sys

pygame.init()

TILE_SIZE = 32
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cave Platformer")
clock = pygame.time.Clock()

def load_level(path):
    with open(path) as file:
        lines = file.readlines()
        return [[int(char) for char in line.strip().split()] for line in lines]


tile_images = {
    1: pygame.image.load("game/assets/floor.png").convert_alpha(),
    2: pygame.image.load("game/assets/wall.png").convert_alpha(),
}

def draw_level(level_data):
    for y, row in enumerate(level_data):
        for x, tile in enumerate(row):
            if tile in tile_images:
                screen.blit(tile_images[tile], (x * TILE_SIZE, y * TILE_SIZE))

level_data = load_level("game/levels/level1.txt")

running = True
while running:
    clock.tick(60)  # 60 FPS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))  # clear screen
    draw_level(level_data)
    pygame.display.flip()

pygame.quit()
sys.exit()
