class Grid:
    def __init__(self, width=20, height=20):
        self.width = width
        self.height = height
        self.grid = self._create_empty_grid()

    def _create_empty_grid(self):
        return [['0' for _ in range(self.width)] for _ in range(self.height)]

    def display(self):
        for row in self.grid:
            print(' '.join(row))

