# game_states/gameplay.py

import pygame
from core.base_scene import BaseScene
from settings import BLACK, BLOCK_SIZE, BLOCKS, WIDTH, HEIGHT
from utils.heplers import import_image, import_folder
from game_states.pause import PauseScene  
from utils.sprites import Sprite, CollisionSprite, ExitDoor, Key, Player, Bomb, Coin
from utils.groups import AllSprites
from utils.timer import Timer
from random import choice, choices

class GameplayScene(BaseScene):
    def __init__(self, game, level_data):

        super().__init__(game)
        self.game = game
        self.level_data = level_data
        self.load_assets()
        
        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bomb_sprites = pygame.sprite.Group()    
        self.exit_sprite = pygame.sprite.Group()        
        self.collectible_sprite = pygame.sprite.Group() 
        self.coin_sprite = pygame.sprite.Group() 
        
        self.draw_level()
    
        self.gui_logger = pygame.Surface((500,275), pygame.SRCALPHA)
        self.gui_logger_rect = self.gui_logger.get_rect(topright=(WIDTH-10, 10))
        self.gui_font = pygame.font.Font(None, 24)
        self.gui_font_big = pygame.font.Font(None, 48)
        
        self.remaining_time = 0
        self.countdown_timer = Timer(20000, func = self.countdown, autostart = True, repeat = False)
        self.timer_surface = pygame.Surface((200,50), pygame.SRCALPHA)
        self.timer_surface_rect = self.timer_surface.get_rect(midtop=(WIDTH/2, 10))
        self.game_over_surface = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
        self.game_over_surface_rect = self.game_over_surface.get_rect(center=(WIDTH/2, HEIGHT/2))
        
        self.in_play_coin_count = pygame.Surface((100,50), pygame.SRCALPHA)
        self.in_play_coin_rect = self.in_play_coin_count.get_rect(topleft=(10, 10))
        
        self.coin_image_scaled_down = pygame.transform.scale(self.coin_image, (int(self.coin_image.get_width() * 0.5), int(self.coin_image.get_height() * 0.5)))
        
    
    def load_assets(self):
        self.player_frames = import_folder('images','player')
        self.bomb_frames = import_folder('images','throwable', 'bomb')
        self.coin_image = import_image('images','collectibles','coin')

    def interpolate_color(self, start_color, end_color, factor):
        r = int(start_color[0] * (1 - factor) + end_color[0] * factor)
        g = int(start_color[1] * (1 - factor) + end_color[1] * factor)
        b = int(start_color[2] * (1 - factor) + end_color[2] * factor)
        return (r, g, b)
    
    def countdown(self):
        if self.remaining_time:
            # Calculate the remaining time
            remaining_time = self.countdown_timer.update()  # In milliseconds
            remaining_seconds = remaining_time // 1000  # Convert to seconds
            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60
            
            # Calculate the percentage of remaining time
            if self.countdown_timer.duration > 0:
                remaining_percentage = remaining_time / self.countdown_timer.duration
            else:
                remaining_percentage = 0

            self.timer_surface.fill((0, 0, 0, 0))  
            # Draw the background of the bar
            pygame.draw.rect(
                surface=self.timer_surface,
                color=(255, 255, 255, 50),  
                rect=(0, 0, self.timer_surface.get_width(), self.timer_surface.get_height()), 
                border_radius=10
            )

            start_color = (0, 255, 0)
            end_color = (255, 0, 0)  
            
            current_color = self.interpolate_color(start_color, end_color, 1 - remaining_percentage)
             
            bar_width = self.timer_surface.get_width() * remaining_percentage
            
            pygame.draw.rect(
                surface=self.timer_surface,
                color=current_color,  
                rect=(0, 0, bar_width, self.timer_surface.get_height()),  # Fill up to the calculated width
                border_radius=10
            )

            # Display the remaining time as text in the middle of the bar
            time_text = f"{minutes:02}:{seconds:02}"
            text_surface = self.gui_font.render(time_text, True, (0, 0, 0))  
            text_rect = text_surface.get_rect(center=self.timer_surface.get_rect().center)
            self.timer_surface.blit(text_surface, text_rect.topleft)
    
    def recalculate_coins(self):
        self.in_play_coin_count.fill((0, 0, 0, 0))  
        pygame.draw.rect(
            surface=self.in_play_coin_count,
            color=(255, 255, 255, 50),  
            rect=(0, 0, self.in_play_coin_count.get_width(), self.in_play_coin_count.get_height()), 
            border_radius=10
        )
        
        text_surface = self.gui_font.render(str(self.game.in_play_coin_count), True, (0, 0, 0))  
        text_rect = text_surface.get_rect(center=self.in_play_coin_count.get_rect().center)
        self.in_play_coin_count.blit(text_surface, text_rect.topleft)
        
    def game_over_func(self, screen):
        if not self.remaining_time:
            pygame.draw.rect(
                surface=self.game_over_surface,
                color=(255,255,255, 100),  
                rect=self.game_over_surface.get_rect(),  
                border_radius=10                  
            )
 
            text_surface = self.gui_font_big.render('Game Over', True, (0, 0, 0))
            self.game_over_surface.blit(text_surface, (WIDTH/2, HEIGHT/2))
            screen.blit(self.game_over_surface)

    def log_gui(self):
        pygame.draw.rect(
            surface=self.gui_logger,           
            color=(255,255,255, 100),            
            rect=self.gui_logger.get_rect(),  
            border_radius=10
        )

        GUI_TEXT = (
            f'Game Data: {self.game.level_url}',
            f'Player Position: {self.player.rect.center}',
            f'Key Position: {self.item_position}',
            f'Exit Position: {self.exit_position}',
            f'Key : {"Yes" if self.player.has_key else "No"}',
        )
        for i, text in enumerate(GUI_TEXT):
            text_surface = self.gui_font.render(text, True, (0, 0, 0))
            self.gui_logger.blit(text_surface, (10, 10 + i * 30))
            
    def create_bomb(self, pos, direction):
        x = pos[0] + direction * 34 if direction == 1 else pos[0] + direction * 34 - self.bomb_frames[0].get_width() 
        Bomb(self.bomb_frames, (x, pos[1]), direction, (self.all_sprites, self.bomb_sprites), self.collision_sprites)
   
    def draw_level(self):
        for y, row in enumerate(self.level_data):
            for x, block in enumerate(row):
                block_info = BLOCKS.get(block)
                if block_info:
                    color = pygame.Color(block_info['color'])
                    image =  pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))    
                    image.fill(color)
                    if block_info['name'] == 'wall': 
                        CollisionSprite((x * BLOCK_SIZE, y * BLOCK_SIZE), image, (self.all_sprites, self.collision_sprites))
                    elif block_info['name'] == 'floor':
                        Sprite((x * BLOCK_SIZE, y * BLOCK_SIZE), image, self.all_sprites)
        # for y, row in enumerate(self.level_data):
        #     for x, block in enumerate(row):
        #         block_info = BLOCKS.get(block)
        #         if block_info and block_info['name'] == 'wall':
        #             color = pygame.Color(block_info['color'])
        #             image =  pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))    
        #             image.fill(color)
        #             CollisionSprite((x * BLOCK_SIZE, y * BLOCK_SIZE), image, self.collision_sprites)
                    
        self.exit_position = self.get_exit_spawnable_position()
        self.item_position = self.get_item_spawnable_position()
        self.player_position = self.get_player_spawnable_position()
        self.coin_positions = self.get_coin_spawnable_position()
        
        for pos in self.coin_positions:
            Coin(pos, (self.all_sprites, self.coin_sprite), self.coin_image)        
        
        self.exit_door = ExitDoor(self.exit_position, (self.all_sprites, self.exit_sprite))
        self.exit_key = Key(self.item_position, (self.all_sprites, self.collectible_sprite))
        self.player = Player(
            self.player_position, 
            self.all_sprites, 
            self.collision_sprites, 
            self.exit_sprite, 
            self.collectible_sprite, 
            self.coin_sprite,
            self.player_frames, 
            self.create_bomb,
            self.game,
            self.get_new_level,
        )   

    def get_new_level(self):
        print('requesting new level')
        self.all_sprites.empty()
        self.collision_sprites.empty()
        self.exit_sprite.empty()
        self.collectible_sprite.empty()
        self.coin_sprite.empty()
        from game_states.loadgame import LoadGame
        self.game.scene_manager.go_to(LoadGame(self.game, self.game.level_url))
        
    def get_player_spawnable_position(self):
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
    
    def get_exit_spawnable_position(self):
        potential_positions = []
        for y in range(len(self.level_data) - 1):  
            for x in range(len(self.level_data[y])):
                if (self.level_data[y][x] == 1 and self.level_data[y + 1][x] == 1):
                    # Store the position of the top cell of the 2x1 space
                    potential_positions.append((x*BLOCK_SIZE, y*BLOCK_SIZE))
        if potential_positions:
            return choice(potential_positions)
    
    def get_item_spawnable_position(self):
        potential_positions = []
        for y in range(len(self.level_data)): 
            for x in range(len(self.level_data[y])):
                if self.level_data[y][x] == 1:  # Check if the cell is a floor
                    # Store the position of the cell
                    potential_positions.append((x * BLOCK_SIZE, y * BLOCK_SIZE))
        
        if potential_positions:
            # Create a list of weights (for simplicity, all weights are equal)
            weights = [1] * len(potential_positions)
            return choices(potential_positions, weights=weights, k=1)[0]  # Select one position based on weights
        return None  # Return None if no spawnable position was found
    
    def get_coin_spawnable_position(self):
        potential_positions = []
        for y in range(len(self.level_data)): 
            for x in range(len(self.level_data[y])):
                if self.level_data[y][x] == 1:  # Check if the cell is a floor
                    # Store the position of the cell
                    potential_positions.append((x * BLOCK_SIZE, y * BLOCK_SIZE))
        
        if potential_positions:
            # Create a list of weights (for simplicity, all weights are equal)
            weights = [1] * len(potential_positions)
            return choices(potential_positions, weights=weights, k=10) # Select one position based on weights
        return None  # Return None if no spawnable position was found
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.paused = True
                self.game.scene_manager.go_to(PauseScene(self.game))
    
    def update(self):
        pass
    
    def draw(self, screen):
        screen.fill(BLACK)
        
        self.remaining_time = self.countdown_timer.update()//1000 if self.countdown_timer else 0
        self.all_sprites.update(self.game.dt) 
        self.countdown_timer.update()
        
        self.all_sprites.draw(self.player.rect.center)
        self.log_gui()
        self.countdown()
        self.recalculate_coins()
        self.game_over_func(screen)
        
        screen.blit(self.gui_logger,  self.gui_logger.get_rect(topright=(WIDTH - 10, 10)))
        screen.blit(self.timer_surface, self.timer_surface_rect)
        
        screen.blit(self.in_play_coin_count, self.in_play_coin_rect)
        
