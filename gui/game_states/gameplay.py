# game_states/gameplay.py

import pygame
from core.base_scene import BaseScene
from settings import BLACK
from utils.heplers import import_image, import_folder
from game_states.pause import PauseScene  

class GameplayScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        
        if not self.game.paused:
            print('game started')
        else:
            print('game resumed')
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.paused = True
                self.game.scene_manager.go_to(PauseScene(self.game))
    
    def update(self):
        pass

    def draw(self, screen):
        screen.fill(BLACK)
