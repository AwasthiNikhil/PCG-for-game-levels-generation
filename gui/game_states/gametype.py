# game_states/gametype.py
import pygame
from core.base_scene import BaseScene
from utils.button import Button
from settings import WHITE
from settings import WIDTH, HEIGHT

class SelectGameTypeScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("Arial", 24)
        self.buttons = []
        
        self.create_buttons()
        

    def create_buttons(self):
        button_width = 250
        button_height = 40
        button_margin = 25
        initial_y = 100 
        x_pos = WIDTH / 2 - button_width / 2
        self.button_callbacks = {
            "Random": self.go_back,
            "Perlin": self.go_back,
            "Simplex": self.go_back,
            "Cellular Automata": self.go_back,
            "Binary Space Partitioning": self.go_back,
            "Graph": self.go_back,
            "Back": self.go_back
        }

        for idx, (label, callback) in enumerate(self.button_callbacks.items()):
            y_pos = initial_y + (button_height + button_margin) * idx
            self.buttons.append(Button(label, (x_pos, y_pos), (button_width, button_height), callback, self.font))
        

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


