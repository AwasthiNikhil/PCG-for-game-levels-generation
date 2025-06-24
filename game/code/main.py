from settings import *
from levelloader import *
from sprites import *
from groups import *
from support import *

class Game():
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        pygame.display.set_caption('Game')
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()        
                
        # load game
        self.load_assets()
        self.setup()
        
    def load_assets(self):
        self.player_frames = import_folder('images','player')
        
    def setup(self):
        self.level_loader = LevelLoader('../output')
        self.level_data = self.level_loader.get_grid()
        
        for y, row in enumerate(self.level_data):
            for x, block in enumerate(row):
                block_info = BLOCKS.get(block)
                if block_info:  # Ensure it's a valid block
                    color = pygame.Color(block_info['color'])
                    image =  pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))    
                    image.fill(color)
                    Sprite((x * BLOCK_SIZE, y * BLOCK_SIZE), image, self.all_sprites)
        
        for y, row in enumerate(self.level_data):
            for x, block in enumerate(row):
                block_info = BLOCKS.get(block)
                if block_info and block_info['name'] == 'wall':
                    color = pygame.Color(block_info['color'])
                    image =  pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))    
                    image.fill(color)
                    CollisionSprite((x * BLOCK_SIZE, y * BLOCK_SIZE), image, self.collision_sprites)
                
                        
                
        # TODO: Find first 2*2 ground block where player can spawn 
        self.player = Player(self.get_spawnable_player_position(), self.all_sprites, self.collision_sprites, self.player_frames)    
      
    def get_spawnable_player_position(self):
        for y in range(len(self.level_data) - 1):  
            for x in range(len(self.level_data[y]) - 1): 
                if (self.level_data[y][x] == 1 and
                    self.level_data[y][x + 1] == 1 and
                    self.level_data[y + 1][x] == 1 and
                    self.level_data[y + 1][x + 1] == 1):
                    # Return the top-left corner of the found 2x2 area
                    return (x*BLOCK_SIZE, y*BLOCK_SIZE)
        # Return None if no spawnable position was found
        return None

        
    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            # update
            self.display_surface.fill('black')
            self.all_sprites.update(dt) 
                
            # draw
            self.all_sprites.draw(self.player.rect.center)
            pygame.display.update()
            
            
        
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
