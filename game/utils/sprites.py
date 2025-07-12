from settings import *
import pygame
from utils.timer import Timer
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
        self.type = 'wall'

class AnimatedSprite(Sprite):
    def __init__(self, frames, pos, groups):
        self.frames, self.frame_index, self.animation_speed = frames, 0, 10
        super().__init__(pos, self.frames[self.frame_index], groups)

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]

class Player(AnimatedSprite):
    def __init__(self, pos, groups, collision_sprites, exit_sprite, collectible_sprite, coin_sprite, frames, create_bomb, game, get_new_level=None):

        super().__init__(frames, pos, groups)
        self.type = 'object'
        self.create_bomb = create_bomb
        self.flip = False
        self.game= game
        
        
        self.get_new_level = get_new_level
        
        # movement and collision
        self.direction = pygame.Vector2()
        self.collision_sprites = collision_sprites
        self.exit_sprite = exit_sprite
        self.collectible_sprite = collectible_sprite
        self.coin_sprite = coin_sprite
        self.speed = 600
        self.gravity = 10
        self.on_floor = False
        self.has_key = False        
        self.bomb_shoot_timer = Timer(500)

    def input(self):
        keys = pygame.key.get_pressed()
        controls = self.game.settings['CONTROLS'] 
        move_left_key = controls.get('MOVE_LEFT', pygame.K_a)
        move_right_key = controls.get('MOVE_RIGHT', pygame.K_d)
        jump_key = controls.get('JUMP', pygame.K_w)
        shoot_key = controls.get('SHOOT', pygame.K_SPACE) 
        self.direction.x = int(keys[move_right_key]) - int(keys[move_left_key])
        if keys[jump_key] and self.on_floor:
            self.direction.y = -12
        if keys[shoot_key] and not self.bomb_shoot_timer: 
            self.create_bomb(self.rect.center, -1 if self.flip else 1)
            self.bomb_shoot_timer.activate()
        
    def move(self, dt):
        # horizontal
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
        for sprite in self.coin_sprite:
            if sprite.rect.colliderect(self.rect):
                self.game.in_play_coin_count = self.game.in_play_coin_count + 1
                print(self.game.in_play_coin_count)
                sprite.kill()
    
    def check_finish(self):
        if self.has_key:
            for sprite in self.exit_sprite:
                if sprite.rect.colliderect(self.rect):
                    print('Completed this level!')
                    sprite.kill()
                    self.get_new_level()
    
    def update(self, dt):   
        self.bomb_shoot_timer.update()
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
    def __init__(self, surf, pos, direction, groups, collision_sprites):
        super().__init__(pos, surf[0], groups)
        self.collision_sprites = collision_sprites
        self.has_exploded = False
        
        # adjustment
        self.image = pygame.transform.flip(self.image, direction == -1, False)
        
        #movement
        self.direction = direction
        self.speed = 850
        self.velocity = pygame.math.Vector2(300, -400) 
        self.gravity = 800  # Pixels per second^2
    
    def update(self, dt):     
        # Update velocity with gravity
        self.velocity.y += self.gravity * dt

        # Update position using velocity
        self.rect.centerx += self.direction * self.velocity.x * dt
        self.rect.centery += self.velocity.y * dt
        if not self.has_exploded:
            collided_sprites = pygame.sprite.spritecollide(self, self.collision_sprites, False) 
            if collided_sprites:
                self.has_exploded = True
                explosion_center = self.rect.center
                
                for sprite in self.collision_sprites:
                    if abs(sprite.rect.centerx - explosion_center[0]) < BLOCK_SIZE * 1.5 and \
                        abs(sprite.rect.centery - explosion_center[1]) < BLOCK_SIZE * 1.5:
                            # sprite.kill()
                            floor_info = BLOCKS.get(1)
                            if floor_info:
                                floor_color = pygame.Color(floor_info['color'])
                                new_image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
                                new_image.fill(floor_color) 
                                sprite.image = new_image 
                                sprite.type = 'ground' 
                                print(f"Changed sprite at {sprite.rect.topleft} to floor color: {floor_color}") 
                            sprite.remove(self.collision_sprites)
                            
                            
                self.kill()
