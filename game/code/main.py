from settings import *
# from levelloader import *
from levelloader2 import *
from sprites import *
from groups import *

class Game():
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        pygame.display.set_caption('Game')
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()        
        
        # lvl = LevelLoader('../output',self.all_sprites)
        
        self.setup()
        
    def setup(self):
        self.level_data = LevelLoader2('../output')
        
        for y, row in enumerate(self.level_data.get_grid()):
            for x, block in enumerate(row):
                block_info = BLOCKS.get(block)
                if block_info:  # Ensure it's a valid block
                    color = pygame.Color(block_info['color'])
                    image =  pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))    
                    image.fill(color)
                    Sprite((x * BLOCK_SIZE, y * BLOCK_SIZE), image, self.all_sprites)
        
        for y, row in enumerate(self.level_data.get_grid()):
            for x, block in enumerate(row):
                block_info = BLOCKS.get(block)
                if block_info and block_info['name'] == 'wall':
                    color = pygame.Color(block_info['color'])
                    image =  pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))    
                    image.fill(color)
                    CollisionSprite((x * BLOCK_SIZE, y * BLOCK_SIZE), image, self.collision_sprites)
                
        # TODO: Find first 2*2 ground block where player can spawn 
        self.player = Player((600,300), self.all_sprites, self.collision_sprites)    
        

        
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
