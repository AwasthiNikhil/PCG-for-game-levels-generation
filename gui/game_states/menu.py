# game_states/menu.py

import pygame
from core.base_scene import BaseScene
from utils.button import Button
from settings import WIDTH, HEIGHT, BLUE
from game_states.gameplay import GameplayScene
from game_states.options import OptionsScene

class MenuScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.buttons = []
        self.font = pygame.font.SysFont("Arial", 30)
        self.title_font = pygame.font.SysFont("Comic Sans MS", 72, bold=True)  
        # self.title_font = pygame.font.Font("assets/fonts/HappyMonkey.ttf", 72)
        self.create_buttons()

    def create_buttons(self):
        start_btn = Button("Start Game", (WIDTH/2 - 100, 250), (200, 50), self.start_game)
        options_btn = Button("Options", (WIDTH/2 - 100, 320), (200, 50), self.open_options)
        quit_btn = Button("Quit", (WIDTH/2 - 100, 390), (200, 50), self.quit_game)

        self.buttons.extend([start_btn,  options_btn, quit_btn])

    def start_game(self):
        self.game.scene_manager.go_to(GameplayScene(self.game))

    def open_options(self):
        self.game.scene_manager.go_to(OptionsScene(self.game))
        
    def quit_game(self):
        pygame.quit()
        exit()


    def handle_events(self, events):
        for event in events:
            for btn in self.buttons:
                btn.handle_event(event)

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(BLUE)

        title_surface = self.title_font.render("Lucky You", True, 'white')
        title_rect = title_surface.get_rect(center=(WIDTH // 2, 120))
        screen.blit(title_surface, title_rect)

        for btn in self.buttons:
            btn.draw(screen)

