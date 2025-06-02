import random
from classes.bsp.BSPNodeRoom import BSPNode

class BSPLevelGenerator:
    def __init__(self, grid, min_leaf_size=6, max_leaf_size=20):
            self.grid = grid
            self.min_leaf_size = min_leaf_size
            self.max_leaf_size = max_leaf_size
            self.floor_char = '1'
            self.wall_char = '2'
            self.rooms = []

    def generate(self, seed=None):
        if seed is not None:
            random.seed(seed)
        else:
            seed = random.randint(0, 1000)
            random.seed(seed)

        print(f'seed:{seed}')

        # Fill grid with walls
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                self.grid.grid[y][x] = self.wall_char

        root = BSPNode(0, 0, self.grid.width, self.grid.height)
        leaves = root.split(self.min_leaf_size, self.max_leaf_size)

        for leaf in leaves:
            room = leaf.create_room()
            if room:
                self.rooms.append(room)
                self._carve_room(room)

        # Connect rooms
        for i in range(1, len(self.rooms)):
            room_a = self.rooms[i - 1]
            room_b = self.rooms[i]
            self._carve_corridor(room_a.center(), room_b.center())

    def _carve_room(self, room):
        for y in range(room.y, room.y + room.h):
            for x in range(room.x, room.x + room.w):
                self.grid.grid[y][x] = self.floor_char

    def _carve_corridor(self, a, b):
        x1, y1 = a
        x2, y2 = b
        if random.random() < 0.5:
            self._carve_h_corridor(x1, x2, y1)
            self._carve_v_corridor(y1, y2, x2)
        else:
            self._carve_v_corridor(y1, y2, x1)
            self._carve_h_corridor(x1, x2, y2)

    def _carve_h_corridor(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.grid.grid[y][x] = self.floor_char

    def _carve_v_corridor(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.grid.grid[y][x] = self.floor_char
            
