import random

class RandomLevelGenerator:
    def __init__(self, grid, wall_prob=0.3):
        self.grid = grid
        self.wall_prob = wall_prob
        self.floor_char = '1'
        self.wall_char = '2'

    def generate(self, seed=None):
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                # todo
                # check different methods for randomization, use seeds
                if random.random() < self.wall_prob:
                    self.grid.grid[y][x] = self.wall_char
                else:
                    self.grid.grid[y][x] = self.floor_char
