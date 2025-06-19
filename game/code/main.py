from settings import *
from levelloader import *
from player import *

class Game():
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        pygame.display.set_caption('Game')
        
        self.clock = pygame.time.Clock()
        
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()        
        
        lvl = LevelLoader('../output',self.all_sprites)
        player = Player((400, 300), self.all_sprites)
        
        self.running = True
    
    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            self.display_surface.fill('black')
            self.all_sprites.update(dt) 
                
            self.all_sprites.draw(self.display_surface)
            pygame.display.update()
        
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
