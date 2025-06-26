import random
class CellularAutomataLevelGenerator:
    def __init__(self, grid, fill_percent=0.55, iterations=1):
        self.grid = grid
        self.fill_percent = fill_percent  # Initial wall chance
        self.iterations = iterations
        self.floor_char = '1'
        self.wall_char = '2'

    def generate(self, seed=None):
        if seed is not None:
            random.seed(seed)
        else:
            seed = random.randint(0, 1000)
            random.seed(seed)

        print(f'seed:{seed}')

        # Initial random fill
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                if self._is_border(x, y):
                    self.grid.grid[y][x] = self.wall_char
                else:
                    if random.random() < self.fill_percent:
                        self.grid.grid[y][x] = self.wall_char
                    else:
                        self.grid.grid[y][x] = self.floor_char

        # Apply CA rules
        for i in range(self.iterations):
            new_grid = [[self.floor_char for _ in range(self.grid.width)] for _ in range(self.grid.height)]

            for y in range(self.grid.height):
                for x in range(self.grid.width):
                    wall_count = self._count_wall_neighbors(x, y)

                    if self._is_border(x, y):
                        new_grid[y][x] = self.wall_char
                    elif wall_count >= 5:
                        new_grid[y][x] = self.wall_char
                    else:
                        new_grid[y][x] = self.floor_char

            self.grid.grid = new_grid

    def _is_border(self, x, y):
        return x == 0 or y == 0 or x == self.grid.width - 1 or y == self.grid.height - 1

    def _count_wall_neighbors(self, x, y):
        wall_count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx = x + dx
                ny = y + dy
                if 0 <= nx < self.grid.width and 0 <= ny < self.grid.height:
                    if self.grid.grid[ny][nx] == self.wall_char:
                        wall_count += 1
                else:
                    wall_count += 1  # Treat out-of-bounds as walls
        return wall_count
