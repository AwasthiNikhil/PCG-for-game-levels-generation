import random

class GraphLevelGenerator:
    def __init__(self, grid, max_rooms=15, room_min_size=8, room_max_size=16):
        # todo: check edge cases like min cells cant contain max room etc 
        self.grid = grid
        self.max_rooms = max_rooms
        self.room_min_size = room_min_size
        self.room_max_size = room_max_size
        self.rooms = []

    def generate(self, seed=None):
        if seed is not None:
            random.seed(seed)
        else:
            seed = random.randint(0, 1000)
            random.seed(seed)
        print(f'seed:{seed}')

        self._generate_rooms()
        self._connect_rooms()
        self._fill_empty_with_walls()

    def _generate_rooms(self):
        attempts = 0
        while len(self.rooms) < self.max_rooms and attempts < self.max_rooms * 10:
            w = random.randint(self.room_min_size, self.room_max_size)
            h = random.randint(self.room_min_size, self.room_max_size)
            x = random.randint(1, self.grid.width - w - 2)
            y = random.randint(1, self.grid.height - h - 2)
            new_room = (x, y, w, h)

            if self._room_overlaps(new_room):
                attempts += 1
                continue

            self.rooms.append(new_room)
            self._carve_room(new_room)

    def _room_overlaps(self, new_room):
        x1, y1, w1, h1 = new_room
        for room in self.rooms:
            x2, y2, w2, h2 = room
            if (x1 < x2 + w2 and x1 + w1 > x2 and
                y1 < y2 + h2 and y1 + h1 > y2):
                return True
        return False

    def _carve_room(self, room):
        x, y, w, h = room
        for i in range(y, y + h):
            for j in range(x, x + w):
                self.grid.grid[i][j] = '1'  # floor

    def _connect_rooms(self):
        if not self.rooms:
            return

        for i in range(1, len(self.rooms)):
            (x1, y1, w1, h1) = self.rooms[i - 1]
            (x2, y2, w2, h2) = self.rooms[i]

            cx1, cy1 = x1 + w1 // 2, y1 + h1 // 2
            cx2, cy2 = x2 + w2 // 2, y2 + h2 // 2

            if random.random() < 0.5:
                self._carve_h_corridor(cx1, cx2, cy1)
                self._carve_v_corridor(cy1, cy2, cx2)
            else:
                self._carve_v_corridor(cy1, cy2, cx1)
                self._carve_h_corridor(cx1, cx2, cy2)

    def _carve_h_corridor(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.grid.grid[y][x] = '1'

    def _carve_v_corridor(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.grid.grid[y][x] = '1'

    def _fill_empty_with_walls(self):
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                if self.grid.grid[y][x] == ' ':
                    self.grid.grid[y][x] = '2'  # wall
