from settings import *
from math import atan2, degrees

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        self.type = 'ground'

class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)

class AnimatedSprite(Sprite):
    def __init__(self, frames, pos, groups):
        self.frames, self.frame_index, self.animation_speed = frames, 0, 10
        super().__init__(pos, self.frames[self.frame_index], groups)

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]

class Player(AnimatedSprite):
    def __init__(self, pos, groups, collision_sprites, exit_sprite, collectible_sprite, frames, get_new_level):

        super().__init__(frames, pos, groups)
        self.type = 'object'
        self.flip = False
        
        self.get_new_level = get_new_level
        
        # movement and collision
        self.direction = pygame.Vector2()
        self.collision_sprites = collision_sprites
        self.exit_sprite = exit_sprite
        self.collectible_sprite = collectible_sprite
        self.speed = PLAYER_SPEED
        self.gravity = PLAYER_GRAVITY
        self.on_floor = False
        self.has_key = False
    
    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        # self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        # self.direction = self.direction.normalize() if self.direction else self.direction
        
        if keys[pygame.K_SPACE] and self.on_floor:
            self.direction.y = -JUMP
        
    def move(self, dt):
        # horizontak
        self.rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        
        # vertical
        self.direction.y += self.gravity * dt
        self.rect.y += self.direction.y
        self.collision('vertical')
             
    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.rect.right = sprite.rect.left
                    if self.direction.x < 0: self.rect.left = sprite.rect.right
                if direction == 'vertical':
                    if self.direction.y > 0: self.rect.bottom = sprite.rect.top
                    if self.direction.y < 0: self.rect.top = sprite.rect.bottom
                    self.direction.y = 0
        
        self.check_collectible()
        self.check_finish()
        
    def check_floor(self):
        bottom_rect = pygame.FRect((0, 0), (self.rect.width, 2)).move_to(midtop = self.rect.midbottom)
        
        level_rects = [sprite.rect for sprite in self.collision_sprites]
                
        self.on_floor = True if bottom_rect.collidelist(level_rects)>= 0 else False

    def animate(self, dt):
        if self.direction.x:
            self.frame_index += self.animation_speed * dt
            self.flip = self.direction.x < 0
        else:
            self.frame_index = 0
        self.frame_index = 1 if not self.on_floor else self.frame_index

        self.image = self.frames[int(self.frame_index)% len (self.frames)]
        self.image = pygame.transform.flip(self.image, self.flip, False)

    def check_collectible(self):
        for sprite in self.collectible_sprite:
            if sprite.rect.colliderect(self.rect):
                self.has_key = True
                print('collected key :)')
                sprite.kill()
    
    def check_finish(self):
        if self.has_key:
            for sprite in self.exit_sprite:
                if sprite.rect.colliderect(self.rect):
                    print('Completed this level!')
                    sprite.kill()
                    self.get_new_level()
    
    def update(self, dt):   
        self.check_floor()
        self.input()
        self.move(dt)
        self.animate(dt)
    
class ExitDoor(Sprite):
    def __init__(self, pos, groups):
        surf = pygame.image.load(join('images', 'exit_door', '0.png')).convert_alpha()
        super().__init__(pos, surf, groups)
        
        self.type = 'exit'

class Key(Sprite):
    def __init__(self, pos, groups):
        surf = pygame.image.load(join('images', 'key', '0.png')).convert_alpha()
        super().__init__(pos, surf, groups)
        
        self.type = 'exit'
    
