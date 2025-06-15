from settings import *

class LevelLoader(pygame.sprite.Sprite):
    def __init__(self, path, groups):
        super().__init__(groups)
        
        with open(f'{path}.txt', 'r', encoding='utf-16') as file:
            self.level = file.read()
            
        marker = '>>>'
        if marker in self.level:
            self.level = self.level.split(marker, 1)[1].strip()
                    
        # print('Level loaded successfully' if self.level else 'Level not found')
        
        self.grid = self.parse_level(self.level)

        self.width = len(self.grid[0]) * BLOCK_SIZE  # Number of columns * block size
        self.height = len(self.grid) * BLOCK_SIZE # Number of rows * block size
        
        self.image =  pygame.Surface((self.width, self.height))    
        self.rect = self.image.get_frect()

        self.displayLoaded()  # Display the level once the image is created
    
    def parse_level(self, level_data):
        # Converts the level string into a 2D grid (list of lists).
        rows = level_data.split('\n')
        grid = [list(map(int, row.split())) for row in rows if row.strip()]  # Split by spaces and convert to ints
        return grid

    def displayLoaded(self):
        # Displays the level grid on the surface.
        for y, row in enumerate(self.grid):
            for x, block in enumerate(row):
                block_info = BLOCKS.get(block)
                if block_info:  # Ensure it's a valid block
                    color = pygame.Color(block_info['color'])
                    pygame.draw.rect(self.image, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

