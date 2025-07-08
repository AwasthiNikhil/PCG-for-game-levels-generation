import pygame
import random
from collections import deque

# --- Config ---
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 10
GRID_WIDTH = WIDTH // TILE_SIZE
GRID_HEIGHT = HEIGHT // TILE_SIZE

WALL = 1
FLOOR = 0

TARGET_FLOOR_PERCENT = 0.4
NUM_DRUNKARDS = 5  # Number of drunkards walking at once

DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Drunkard's Walk Cave with Connectivity Check")

COLOR_WALL = (30, 30, 30)
COLOR_FLOOR = (200, 200, 200)
COLOR_CONNECTED = (150, 220, 150)  # Optional: color connected area differently

grid = [[WALL for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def in_bounds(x, y):
    return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT

def drunkards_walk():
    # Start drunkards near center, slightly randomized positions
    drunkards = [
        (GRID_WIDTH // 2 + random.randint(-3, 3), GRID_HEIGHT // 2 + random.randint(-3, 3))
        for _ in range(NUM_DRUNKARDS)
    ]
    carved = 0
    target = int(GRID_WIDTH * GRID_HEIGHT * TARGET_FLOOR_PERCENT)

    # Carve starting positions
    for x, y in drunkards:
        if in_bounds(x, y) and grid[y][x] == WALL:
            grid[y][x] = FLOOR
            carved += 1

    while carved < target:
        for i in range(NUM_DRUNKARDS):
            x, y = drunkards[i]
            dx, dy = random.choice(DIRECTIONS)
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny):
                if grid[ny][nx] == WALL:
                    grid[ny][nx] = FLOOR
                    carved += 1
                drunkards[i] = (nx, ny)
            else:
                # Teleport drunkard back near center if out of bounds
                drunkards[i] = (GRID_WIDTH // 2 + random.randint(-3,3), GRID_HEIGHT // 2 + random.randint(-3,3))

def flood_fill(start_x, start_y):
    visited = set()
    queue = deque([(start_x, start_y)])
    visited.add((start_x, start_y))

    while queue:
        x, y = queue.popleft()
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in visited and grid[ny][nx] == FLOOR:
                visited.add((nx, ny))
                queue.append((nx, ny))
    return visited

def connectivity_check():
    # Find any floor tile to start flood fill
    start = None
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] == FLOOR:
                start = (x, y)
                break
        if start:
            break

    if not start:
        return  # no floor carved yet

    connected_region = flood_fill(*start)

    # Convert all floors not connected to the main region back to walls
    disconnected = 0
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] == FLOOR and (x, y) not in connected_region:
                grid[y][x] = WALL
                disconnected += 1

    print(f"Removed {disconnected} disconnected floor tiles.")

    # If there are disconnected regions, try to connect them
    # Simple approach: find walls adjacent to both connected and disconnected regions and carve a tunnel
    while True:
        disconnected_tiles = [
            (x, y) for y in range(GRID_HEIGHT) for x in range(GRID_WIDTH)
            if grid[y][x] == WALL and any(
                in_bounds(x + dx, y + dy) and grid[y + dy][x + dx] == FLOOR and (x + dx, y + dy) in connected_region
                for dx, dy in DIRECTIONS)
            and any(
                in_bounds(x + dx, y + dy) and grid[y + dy][x + dx] == FLOOR and (x + dx, y + dy) not in connected_region
                for dx, dy in DIRECTIONS)
        ]

        if not disconnected_tiles:
            break  # no tiles to connect

        # Carve walls that bridge connected and disconnected floors
        for x, y in disconnected_tiles:
            grid[y][x] = FLOOR

        # Update connected region with flood fill again
        connected_region = flood_fill(*start)

def draw():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            color = COLOR_FLOOR if grid[y][x] == FLOOR else COLOR_WALL
            pygame.draw.rect(screen, color, rect)

def main():
    clock = pygame.time.Clock()
    drunkards_walk()
    connectivity_check()

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
