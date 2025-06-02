import random

class WFCLevelGenerator:
    def __init__(self, grid, tile_rules=None):
        self.grid = grid
        self.tile_types = ['1', '2', '3', '4']  # Floor, Wall, Water, Sand
        self.floor_char = '1'
        self.wall_char = '2'
        self.tile_rules = tile_rules or self._default_tile_rules()
        self.wave = [[set(self.tile_types) for _ in range(grid.width)] for _ in range(grid.height)]

    def generate(self, seed=None):
        if seed is not None:
            random.seed(seed)
        else:
            seed = random.randint(0, 1000)
            random.seed(seed)
        print(f'seed:{seed}')

        while True:
            cell = self._find_lowest_entropy_cell()
            if cell is None:
                break  # all cells collapsed

            y, x = cell
            possible = list(self.wave[y][x])
            chosen = random.choice(possible)
            self.wave[y][x] = {chosen}
            self._propagate(x, y)

        # Apply to grid
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                value = next(iter(self.wave[y][x])) if len(self.wave[y][x]) == 1 else self.wall_char
                self.grid.grid[y][x] = value

    def _find_lowest_entropy_cell(self):
        min_entropy = float('inf')
        best_cells = []

        for y in range(self.grid.height):
            for x in range(self.grid.width):
                options = self.wave[y][x]
                if len(options) == 1:
                    continue
                entropy = len(options)
                if entropy < min_entropy:
                    min_entropy = entropy
                    best_cells = [(y, x)]
                elif entropy == min_entropy:
                    best_cells.append((y, x))

        return random.choice(best_cells) if best_cells else None

    def _propagate(self, x, y):
        queue = [(x, y)]
        while queue:
            cx, cy = queue.pop(0)
            options = self.wave[cy][cx]

            for dx, dy, direction in [(-1, 0, 'W'), (1, 0, 'E'), (0, -1, 'N'), (0, 1, 'S')]:
                nx, ny = cx + dx, cy + dy
                if not (0 <= nx < self.grid.width and 0 <= ny < self.grid.height):
                    continue

                neighbor_options = self.wave[ny][nx]
                allowed = set()
                for t in options:
                    allowed |= set(self.tile_rules[t][direction])

                if neighbor_options.issubset(allowed):
                    continue

                new_options = neighbor_options & allowed
                if not new_options:
                    continue  # contradiction — no action for now

                if new_options != neighbor_options:
                    self.wave[ny][nx] = new_options
                    queue.append((nx, ny))

    def _default_tile_rules(self):
        return {
            '1': {  # Floor
                'N': ['1', '2', '4'],
                'S': ['1', '2', '4'],
                'E': ['1', '2', '4'],
                'W': ['1', '2', '4'],
            },
            '2': {  # Wall
                'N': ['1', '2'],
                'S': ['1', '2'],
                'E': ['1', '2'],
                'W': ['1', '2'],
            },
            '3': {  # Water
                'N': ['3', '4'],
                'S': ['3', '4'],
                'E': ['3', '4'],
                'W': ['3', '4'],
            },
            '4': {  # Sand
                'N': ['3', '4', '1'],
                'S': ['3', '4', '1'],
                'E': ['3', '4', '1'],
                'W': ['3', '4', '1'],
            },
        }
