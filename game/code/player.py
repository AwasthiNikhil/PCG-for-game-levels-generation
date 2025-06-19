from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('images','player','down','0.png'))
        self.rect = self.image.get_frect(center = pos)
        
        self.hitbox_rect = self.rect
        
        #movement
        self.direction = pygame.math.Vector2() 
        self.speed = 500
        
    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        
        self.direction = self.direction.normalize() if self.direction else self.direction
            
    def move(self,dt):
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.rect.center = self.hitbox_rect.center    
    
    def update(self,dt):
        self.input()
        self.move(dt)

