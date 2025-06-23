from settings import *

class LevelLoader2:
    def __init__(self, path):
        
        with open(f'{path}.txt', 'r', encoding='utf-16') as file:
            self.level = file.read()
            
        marker = '>>>'
        if marker in self.level:
            self.level = self.level.split(marker, 1)[1].strip()
                    
        # print('Level loaded successfully' if self.level else 'Level not found')
        
        # 1 floor 
        # 2 wall
        self.grid = self.parse_level(self.level)
    
    def get_grid(self):
        return self.grid
    
    def parse_level(self, level_data):
        # Converts the level string into a 2D grid (list of lists).
        rows = level_data.split('\n')
        grid = [list(map(int, row.split())) for row in rows if row.strip()]  # Split by spaces and convert to ints
        return grid

