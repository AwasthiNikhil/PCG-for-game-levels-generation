# game_states/gameplay.py

import pygame
from core.base_scene import BaseScene
from settings import BLACK
from utils.heplers import import_image, import_folder

class GameplayScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        print('game started')
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                from game_states.menu import MenuScene
                self.game.scene_manager.go_to(MenuScene(self.game))

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(BLACK)
