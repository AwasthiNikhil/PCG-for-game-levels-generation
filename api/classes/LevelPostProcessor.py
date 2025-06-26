class LevelPostProcessor:
    def __init__(self, grid):
        self.grid = grid

    def remove_isolated_walls(self):
        # Check each wall and remove if it's isolated (no neighboring walls)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Adjacent cells (N, S, E, W)
        
        for y in range(1, self.grid.height - 1):
            for x in range(1, self.grid.width - 1):
                if self.grid.grid[y][x] == '2':
                    # Check neighboring cells
                    if not any(self.grid.grid[y + dy][x + dx] == '2' for dx, dy in directions):
                        self.grid.grid[y][x] = '1'  # Remove isolated wall
