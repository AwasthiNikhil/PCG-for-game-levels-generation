import pygame
from os.path import join
from random import randint, uniform

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('game','images','player.png')).convert_alpha()
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        self.direction = pygame.Vector2()
        self.speed = 300
        
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 200
        
        self.mask = pygame.mask.from_surface(self.image)
    
    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True
        
    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d])-int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s])-int(keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed *dt
        
        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites,laser_sprites))
            laser_sound.play()
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, group, surf):
        super().__init__(group)
        self.image = surf
        self.rect = self.image.get_frect(center = (randint(0,WINDOW_WIDTH),randint(0,WINDOW_HEIGHT)))

class Laser(pygame.sprite.Sprite):
    def __init__(self,surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)
    
    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()
        
class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center=pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.direction = pygame.math.Vector2(uniform(-0.5,0.5),1)
        self.speed = randint(400,500)
        self.rotation_speed = randint(0,100)
        self.rotation = 0
    
        
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation,1) 
        self.rect = self.image.get_frect(center=self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)
        
        explosion_sound.play()
    
    def update(self, dt):
        self.frame_index += 40 * dt
        if self.frame_index < len(self.frames):  
            self.image = self.frames[int(self.frame_index)] 
        else:
            self.kill()
        
def collisions():
    global running
    collision_sprite = pygame.sprite.spritecollide(player,meteor_sprites,True,pygame.sprite.collide_mask)
    if collision_sprite:
        print(collision_sprite[0])
        running = False
    for laser in laser_sprites:
        collision_sprites = pygame.sprite.spritecollide(laser,meteor_sprites,True)
        if collision_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames,laser.rect.midtop,all_sprites)
            
def display_scores():
    current_time = pygame.time.get_ticks() // 100
    text_surf = font.render(str(current_time), True, (240,240,240))
    text_rect = text_surf.get_frect(midbottom =( WINDOW_WIDTH/2, WINDOW_HEIGHT - 50))
    
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface,(240,240,240),text_rect.inflate(20,30).move(0,-5),5,10)
    

pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280,720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT ))
pygame.display.set_caption("Game")
running = True
clock = pygame.time.Clock()

# imports
meteor_surf = pygame.image.load(join('game','images','meteor.png')).convert_alpha()
laser_surf = pygame.image.load(join('game','images','laser.png'))
star_surf = pygame.image.load(join('game','images','star.png')).convert_alpha()
font = pygame.font.Font(join('game','images','Oxanium-Bold.ttf'),40)
explosion_frames = [pygame.image.load(join('game','images','explosion',f'{i}.png')) for i in range(21)]

laser_sound = pygame.mixer.Sound(join('game','audio','laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join('game','audio','explosion.wav'))
game_music = pygame.mixer.Sound(join('game','audio','game_music.wav'))

game_music.set_volume(0.3)
game_music.play(loops=-1)

# sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
for i in range(20):
    Star(all_sprites,star_surf)
player = Player(all_sprites)

# custom event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event,200)
    
while running:
    dt = clock.tick()/1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x,y = randint(0,WINDOW_WIDTH), randint(-200,-100)
            Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))
            
    all_sprites.update(dt)
    collisions()
    
    display_surface.fill('#3A2E3F')
    display_scores()
    all_sprites.draw(display_surface)

    pygame.display.update()
    
pygame.quit()
