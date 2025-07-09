from settings import *
import pygame
from os.path import join

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
    def __init__(self, pos, groups, collision_sprites, exit_sprite, collectible_sprite, frames, get_new_level=None):

        super().__init__(frames, pos, groups)
        self.type = 'object'
        self.flip = False
        self.groups = groups
        
        self.get_new_level = get_new_level
        
        # movement and collision
        self.direction = pygame.Vector2()
        self.collision_sprites = collision_sprites
        self.exit_sprite = exit_sprite
        self.collectible_sprite = collectible_sprite
        self.speed = 600
        self.gravity = 10
        self.on_floor = False
        self.has_key = False
    
    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        if keys[pygame.K_w] and self.on_floor:
            self.direction.y = -12
        if pygame.key.get_just_pressed()[pygame.K_SPACE]:
            Bomb(self.rect.center, (self.groups, self.collision_sprites))
        
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
        surf = pygame.image.load(join('assets', 'images', 'exit_door', '0.png')).convert_alpha()
        super().__init__(pos, surf, groups)

        self.type = 'exit'

class Key(Sprite):
    def __init__(self, pos, groups):
        surf = pygame.image.load(join('assets', 'images', 'key', '0.png')).convert_alpha()
        super().__init__(pos, surf, groups)
        
        self.type = 'exit'
    
class Coin(Sprite):
    def __init__(self, pos, groups, image):
        super().__init__(pos, image, groups)
                
        self.type = 'collectible'
        
class Throwable(Sprite):
    def __init__(self, pos, image, groups):
        super().__init__(pos, image, groups)
                
        self.type = 'throwable'


class Bomb(Throwable):
    def __init__(self, pos, groups):
        image = pygame.image.load(join('assets', 'images', 'throwable', 'bomb', '0.png')).convert_alpha()
        super().__init__(pos, image, groups)
        
        self.type = 'bomb'
        self.rect.center = pos
        
        # Physics properties
        self.pos = pygame.math.Vector2(pos)  # Use float precision for motion
        self.velocity = pygame.math.Vector2(300, -400)  # Initial velocity (x, y)
        self.gravity = 800  # Pixels per second^2

    def update(self, dt):
        # Update velocity with gravity
        self.velocity.y += self.gravity * dt

        # Update position using velocity
        self.pos += self.velocity * dt
        self.rect.center = self.pos

        # Remove if out of bounds
        if (self.rect.right < 0 or self.rect.left > WIDTH or
            self.rect.bottom < 0 or self.rect.top > HEIGHT):
            self.kill()