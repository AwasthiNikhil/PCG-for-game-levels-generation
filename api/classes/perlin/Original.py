class NativePerlinLevelGenerator:
    def __init__(self, grid, scale=2.0, threshold=0.0):
        self.grid = grid
        self.scale = scale
        self.threshold = threshold

    def generate(self, seed=None):
        if seed is not None:
            random.seed(seed)
        else:
            seed = random.randint(0, 1000)
            random.seed(seed)
            
        print(f'seed: {seed}')
        grad_table = generate_gradient_table(self.grid.width, self.grid.height)

        # Generate initial grid
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                nx = x / self.scale
                ny = y / self.scale
                n = perlin(nx, ny, grad_table)
                self.grid.grid[y][x] = WALL_CHAR if n < self.threshold else FLOOR_CHAR

        # Generate boundaries
        for x in range(self.grid.width):
            self.grid.grid[0][x] = WALL_CHAR          # Top boundary
            self.grid.grid[self.grid.height-1][x] = WALL_CHAR  # Bottom boundary
        for y in range(self.grid.height):
            self.grid.grid[y][0] = WALL_CHAR          # Left boundary
            self.grid.grid[y][self.grid.width-1] = WALL_CHAR  # Right boundary

        # Pattern conversion pass
        for y in range(1, self.grid.height-1):
            for x in range(1, self.grid.width-1):
                # Check for diagonal patterns
                if (self.grid.grid[y][x] == WALL_CHAR and
                    ((self.grid.grid[y-1][x] == FLOOR_CHAR and self.grid.grid[y][x-1] == FLOOR_CHAR and self.grid.grid[y-1][x-1] == WALL_CHAR) or
                     (self.grid.grid[y+1][x] == FLOOR_CHAR and self.grid.grid[y][x+1] == FLOOR_CHAR and self.grid.grid[y+1][x+1] == WALL_CHAR) or
                     (self.grid.grid[y+1][x] == FLOOR_CHAR and self.grid.grid[y][x-1] == FLOOR_CHAR and self.grid.grid[y+1][x-1] == WALL_CHAR) or
                     (self.grid.grid[y-1][x] == FLOOR_CHAR and self.grid.grid[y][x+1] == FLOOR_CHAR and self.grid.grid[y-1][x+1] == WALL_CHAR))):
                    self.grid.grid[y][x] = FLOOR_CHAR

"""
Alternative pattern definition:
for y in range(self.grid.height-1):
    for x in range(self.grid.width-1):
        # Pattern 1: [[1,2],[2,1]]
        if (self.grid.grid[y][x] == FLOOR_CHAR and 
            self.grid.grid[y][x+1] == WALL_CHAR and
            self.grid.grid[y+1][x] == WALL_CHAR and
            self.grid.grid[y+1][x+1] == FLOOR_CHAR):
            self.grid.grid[y][x+1] = FLOOR_CHAR
            self.grid.grid[y+1][x] = FLOOR_CHAR
            
        # Pattern 2: [[2,1],[1,2]]
        elif (self.grid.grid[y][x] == WALL_CHAR and 
              self.grid.grid[y][x+1] == FLOOR_CHAR and
              self.grid.grid[y+1][x] == FLOOR_CHAR and
              self.grid.grid[y+1][x+1] == WALL_CHAR):
            self.grid.grid[y][x] = FLOOR_CHAR
            self.grid.grid[y+1][x+1] = FLOOR_CHAR
"""
