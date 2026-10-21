import random
from ..settings import *

class RandomLevelGenerator:
    def __init__(self, grid, wall_prob=0.2):
        self.grid = grid
        self.wall_prob = wall_prob

    def generate(self, seed=None):
        # Own generator per call: the same seed gives the same level, and
        # concurrent requests don't share random state.
        self.rng = random.Random(seed)

        # Fill the inner grid with walls and floors
        for y in range(1, self.grid.height - 1):
            for x in range(1, self.grid.width - 1):
                if self.rng.random() < self.wall_prob:
                    self.grid.grid[y][x] = WALL_CHAR
                else:
                    self.grid.grid[y][x] = FLOOR_CHAR


        # boundary
        for x in range(self.grid.width):
            self.grid.grid[0][x-1] = WALL_CHAR  # Top boundary
            self.grid.grid[self.grid.height - 1][x-1] = WALL_CHAR  # Bottom boundary

        for y in range(self.grid.height):
            self.grid.grid[y-1][0] = WALL_CHAR  # Left boundary
            self.grid.grid[y-1][self.grid.width - 1] = WALL_CHAR  # Right boundary

