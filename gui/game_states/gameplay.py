# game_states/gameplay.py

import pygame
from core.base_scene import BaseScene
from settings import BLACK, BLOCK_SIZE, BLOCKS, WIDTH, HEIGHT
from utils.heplers import import_image, import_folder
from game_states.pause import PauseScene  
from utils.sprites import Sprite, CollisionSprite, ExitDoor, Key, Player
from utils.groups import AllSprites
from random import choice, choices

class GameplayScene(BaseScene):
    def __init__(self, game, level_data):
        super().__init__(game)
        self.game = game
        self.level_data = level_data
        self.load_assets()
        
        if not self.game.paused:
            print('game started')
        else:
            print('game resumed')
        
        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.exit_sprite = pygame.sprite.Group()        
        self.collectible_sprite = pygame.sprite.Group()    
        
        self.draw_level()
        
        
        self.gui_logger = pygame.Surface((500,275), pygame.SRCALPHA)
        self.gui_logger_rect = self.gui_logger.get_rect(topright=(WIDTH-10, 10))
        self.gui_font = pygame.font.Font(None, 24)
        self.gui_font_big = pygame.font.Font(None, 48)
        
      
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

    
    def load_assets(self):
        self.player_frames = import_folder('images','player')
        self.bomb_frames = import_folder('images','throwable', 'bomb')
        
    def draw_level(self):
        for y, row in enumerate(self.level_data):
            for x, block in enumerate(row):
                block_info = BLOCKS.get(block)
                if block_info:
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
                    
        self.exit_position = self.get_exit_spawnable_position()
        self.item_position = self.get_item_spawnable_position()
        self.player_position = self.get_player_spawnable_position()

        self.exit_door = ExitDoor(self.exit_position, (self.all_sprites, self.exit_sprite))
        self.exit_key = Key(self.item_position, (self.all_sprites, self.collectible_sprite))
        self.player = Player(
            self.player_position, 
            self.all_sprites, 
            self.collision_sprites, 
            self.exit_sprite, 
            self.collectible_sprite, 
            self.player_frames, 
            self.get_new_level
        )    

    def get_new_level(self):
        print('requesting new level')
        self.all_sprites.empty()
        self.collision_sprites.empty()
        self.exit_sprite.empty()
        self.collectible_sprite.empty()
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
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.paused = True
                self.game.scene_manager.go_to(PauseScene(self.game))
    
    def update(self):
        pass
    
    def draw(self, screen):
        screen.fill(BLACK)
        self.all_sprites.update(self.game.dt) 
        self.all_sprites.draw(self.player.rect.center)
        self.log_gui()
        screen.blit(self.gui_logger,  self.gui_logger.get_rect(topright=(WIDTH - 10, 10)))
        
        
        
