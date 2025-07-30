class Grid:
    def __init__(self, width=20, height=20):
        self.width = width
        self.height = height
        self.grid = self._create_empty_grid()

    def _create_empty_grid(self):
        return [['2' for _ in range(self.width)] for _ in range(self.height)]

    def display(self, return_as_string=False):
        lines = [' '.join(row) for row in self.grid]
        if return_as_string:
            return '\n'.join(lines)
        else:
            for line in lines:
                print(line)
    def get(self, x, y):
        """Safely get the value at grid[y][x] if within bounds."""
        if 0 <= y < self.height and 0 <= x < self.width:
            return self.grid[y][x]
        else:
            raise IndexError(f"Coordinates ({x}, {y}) are out of bounds.")
