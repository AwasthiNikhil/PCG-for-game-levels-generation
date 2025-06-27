# game_states/gameplay.py

import pygame
from core.base_scene import BaseScene
from settings import BLACK

class GameplayScene(BaseScene):
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                from game_states.menu import MenuScene
                self.game.scene_manager.go_to(MenuScene(self.game))

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(BLACK)
