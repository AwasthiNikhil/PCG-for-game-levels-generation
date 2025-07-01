# Leaderboard:
# game_states/gametype.py
import pygame
from core.base_scene import BaseScene
from utils.button import Button
from settings import WHITE
from settings import WIDTH, HEIGHT

class Leaderboard(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("Arial", 24)
        self.buttons = []
        
        # TODO : Dynamic later
        self.back_button = Button("Back", (WIDTH/2 - 40, HEIGHT - 50), (80, 40), self.go_back, self.font)        
        self.buttons.append(self.back_button)
        
        self.display_leaderboard()
        

    def display_leaderboard(self):
        pass
        

    def go_back(self):
        from game_states.menu import MenuScene
        self.game.scene_manager.go_to(MenuScene(self.game))

    def handle_events(self, events):
        for event in events:
            for button in self.buttons:
                button.handle_event(event)

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(WHITE)

        for button in self.buttons:
            button.draw(screen)


