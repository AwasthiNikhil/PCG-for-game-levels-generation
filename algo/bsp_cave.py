import pygame
import random

# --- Config ---
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 10
GRID_WIDTH = WIDTH // TILE_SIZE
GRID_HEIGHT = HEIGHT // TILE_SIZE

WALL = 2
FLOOR = 1

MIN_ROOM_SIZE = 6
MAX_ROOM_SIZE = 15
MAX_LEAF_SIZE = 20

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BSP Cave Generator")

COLOR_WALL = (30, 30, 30)
COLOR_FLOOR = (200, 200, 200)

grid = [[WALL for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

class Leaf:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.left_child = None
        self.right_child = None
        self.room = None
        self.corridors = []

    def split(self):
        # Can't split if already split
        if self.left_child or self.right_child:
            return False

        # Decide split direction
        split_h = random.choice([True, False])
        if self.width > self.height and self.width / self.height >= 1.25:
            split_h = False
        elif self.height > self.width and self.height / self.width >= 1.25:
            split_h = True

        max_split = (self.height if split_h else self.width) - MIN_ROOM_SIZE
        if max_split <= MIN_ROOM_SIZE:
            return False

        split = random.randint(MIN_ROOM_SIZE, max_split)

        if split_h:
            self.left_child = Leaf(self.x, self.y, self.width, split)
            self.right_child = Leaf(self.x, self.y + split, self.width, self.height - split)
        else:
            self.left_child = Leaf(self.x, self.y, split, self.height)
            self.right_child = Leaf(self.x + split, self.y, self.width - split, self.height)

        return True

    def create_rooms(self):
        if self.left_child or self.right_child:
            if self.left_child:
                self.left_child.create_rooms()
            if self.right_child:
                self.right_child.create_rooms()
            if self.left_child and self.right_child:
                room1 = self.left_child.get_room()
                room2 = self.right_child.get_room()
                if room1 and room2:
                    create_corridor_between(room1, room2)
        else:
            # Check if leaf is big enough to create a room
            max_room_w = min(MAX_ROOM_SIZE, self.width - 2)
            max_room_h = min(MAX_ROOM_SIZE, self.height - 2)
            if max_room_w < MIN_ROOM_SIZE or max_room_h < MIN_ROOM_SIZE:
                # Leaf too small for room, skip room creation
                return
            
            room_size_w = random.randint(MIN_ROOM_SIZE, max_room_w)
            room_size_h = random.randint(MIN_ROOM_SIZE, max_room_h)
            room_x = random.randint(self.x + 1, self.x + self.width - room_size_w - 1)
            room_y = random.randint(self.y + 1, self.y + self.height - room_size_h - 1)
            self.room = pygame.Rect(room_x, room_y, room_size_w, room_size_h)
            carve_room(self.room)

    def get_room(self):
        if self.room:
            return self.room
        else:
            rooms = []
            if self.left_child:
                left_room = self.left_child.get_room()
                if left_room:
                    rooms.append(left_room)
            if self.right_child:
                right_room = self.right_child.get_room()
                if right_room:
                    rooms.append(right_room)
            if rooms:
                return random.choice(rooms)
            else:
                return None

def carve_room(room):
    for y in range(room.top, room.top + room.height):
        for x in range(room.left, room.left + room.width):
            grid[y][x] = FLOOR

def create_corridor_between(room1, room2):
    # Connect two rooms with corridors (horizontal then vertical or vice versa)
    x1, y1 = room1.center
    x2, y2 = room2.center

    if random.choice([True, False]):
        # Horizontal then vertical
        carve_h_corridor(x1, x2, y1)
        carve_v_corridor(y1, y2, x2)
    else:
        # Vertical then horizontal
        carve_v_corridor(y1, y2, x1)
        carve_h_corridor(x1, x2, y2)

def carve_h_corridor(x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        grid[y][x] = FLOOR

def carve_v_corridor(y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        grid[y][x] = FLOOR

def draw():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            color = COLOR_FLOOR if grid[y][x] == FLOOR else COLOR_WALL
            pygame.draw.rect(screen, color, rect)

def main():
    root_leaf = Leaf(0, 0, GRID_WIDTH, GRID_HEIGHT)
    leaves = [root_leaf]

    did_split = True
    # Split leaves until no more splits possible
    while did_split:
        did_split = False
        new_leaves = []
        for leaf in leaves:
            if leaf.width > MAX_LEAF_SIZE or leaf.height > MAX_LEAF_SIZE or random.random() > 0.5:
                if leaf.split():
                    new_leaves.append(leaf.left_child)
                    new_leaves.append(leaf.right_child)
                    did_split = True
                else:
                    new_leaves.append(leaf)
            else:
                new_leaves.append(leaf)
        leaves = new_leaves

    # Create rooms
    root_leaf.create_rooms()

    clock = pygame.time.Clock()
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
