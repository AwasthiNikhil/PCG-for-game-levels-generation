# game_states/menu.py

import pygame
from core.base_scene import BaseScene
from utils.button import Button
from settings import WIDTH, HEIGHT, BLUE
# from game_states.gameplay import GameplayScene
from game_states.gametype import SelectGameTypeScene
from game_states.options import OptionsScene
from game_states.leaderboard import Leaderboard

class MenuScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("Arial", 30)
        self.title_font = pygame.font.SysFont("Comic Sans MS", 72, bold=True)  
        self.buttons = []
        
        self.create_buttons()

    def create_buttons(self):
        button_width = 200
        button_height = 50
        button_margin = 20  
        initial_y = 250 
        x_pos = WIDTH / 2 - button_width / 2
        
        self.main_buttons = {
            "Start Game": self.start_game,
            "Leaderboard": self.open_leaderboard,
            "Options": self.open_options,
            "Quit": self.quit_game
        }

        for idx, (label, callback) in enumerate(self.main_buttons.items()):
            y_pos = initial_y + (button_height + button_margin) * idx
            self.buttons.append(Button(label, (x_pos, y_pos), (button_width, button_height), callback, self.font))
        
    def start_game(self):
        # self.game.scene_manager.go_to(GameplayScene(self.game))
        self.game.scene_manager.go_to(SelectGameTypeScene(self.game))
        
    def open_leaderboard(self):
        # self.game.scene_manager.go_to(GameplayScene(self.game))
        self.game.scene_manager.go_to(Leaderboard(self.game))

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

