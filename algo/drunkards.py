import pygame
import random

# --- Config ---
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 10
GRID_WIDTH = WIDTH // TILE_SIZE
GRID_HEIGHT = HEIGHT // TILE_SIZE

WALL = 1
FLOOR = 0

# Percentage of map to carve
TARGET_FLOOR_PERCENT = 0.4

# Directions: up, down, left, right
DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]

# --- Initialize pygame ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Drunkard's Walk Cave Generator")

# Colors
COLOR_WALL = (30, 30, 30)
COLOR_FLOOR = (200, 200, 200)

# --- Create grid full of walls ---
grid = [[WALL for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def in_bounds(x, y):
    return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT

def drunkards_walk():
    # Start in the middle
    x, y = GRID_WIDTH // 2, GRID_HEIGHT // 2
    grid[y][x] = FLOOR
    carved = 1
    target = int(GRID_WIDTH * GRID_HEIGHT * TARGET_FLOOR_PERCENT)

    while carved < target:
        dx, dy = random.choice(DIRECTIONS)
        nx, ny = x + dx, y + dy
        if in_bounds(nx, ny):
            if grid[ny][nx] == WALL:
                grid[ny][nx] = FLOOR
                carved += 1
            x, y = nx, ny
        else:
            # If out of bounds, teleport back to center
            x, y = GRID_WIDTH // 2, GRID_HEIGHT // 2

def draw():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            color = COLOR_FLOOR if grid[y][x] == FLOOR else COLOR_WALL
            pygame.draw.rect(screen, color, rect)

def main():
    clock = pygame.time.Clock()
    drunkards_walk()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        draw()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
