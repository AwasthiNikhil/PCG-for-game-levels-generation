# game_states/gametype.py
import pygame
from core.base_scene import BaseScene
from utils.button import Button
from settings import WHITE
from settings import WIDTH, HEIGHT
from game_states.customizemenu import CustomizeMenuScene

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
        
        customize_menu_options = {
            'random': {
                'width': {'value': 30, 'type': 'slider', 'min': 10, 'max': 100, 'step': 1},
                'height': {'value': 30, 'type': 'slider', 'min': 10, 'max': 100, 'step': 1},
                'seed': {'value': None, 'type': 'input'},
                'wall_probability': {'value': 0.2, 'type': 'slider', 'min': 0.0, 'max': 100, 'step': 1},
            },
            'perlin': {
                'width': {'value': 30, 'type': 'slider', 'min': 10, 'max': 100, 'step': 1},
                'height': {'value': 30, 'type': 'slider', 'min': 10, 'max': 100, 'step': 1},
                'seed': {'value': None, 'type': 'input'},
                'scale': {'value': 2, 'type': 'slider', 'min': 1, 'max': 10, 'step': 0.1},
                'threshold': {'value': 0, 'type': 'slider', 'min': 0, 'max': 1, 'step': 0.1},
                'min_room_size': {'value': 4, 'type': 'slider', 'min': 1, 'max': 20, 'step': 1},
            },
            'simplex': {
                'width': {'value': 30, 'type': 'slider', 'min': 10, 'max': 100, 'step': 1},
                'height': {'value': 30, 'type': 'slider', 'min': 10, 'max': 100, 'step': 1},
                'seed': {'value': None, 'type': 'input'},
                'scale': {'value': 2, 'type': 'slider', 'min': 1, 'max': 10, 'step': 0.1},
                'threshold': {'value': 0, 'type': 'slider', 'min': 0, 'max': 100, 'step': 1},
            },
            'cellular': {
                'width': {'value': 30, 'type': 'slider', 'min': 10, 'max': 100, 'step': 1},
                'height': {'value': 30, 'type': 'slider', 'min': 10, 'max': 100, 'step': 1},
                'seed': {'value': None, 'type': 'input'},
                'wall_probability': {'value': 0.55, 'type': 'slider', 'min': 0, 'max': 100, 'step': 1},
                'iterations': {'value': 1, 'type': 'slider', 'min': 1, 'max': 10, 'step': 1},
            },
            'bSP': {
                'width': {'value': 30, 'type': 'slider', 'min': 10, 'max': 100, 'step': 1},
                'height': {'value': 30, 'type': 'slider', 'min': 10, 'max': 100, 'step': 1},
                'seed': {'value': None, 'type': 'input'},
                'min_leaf_size': {'value': 6, 'type': 'slider', 'min': 1, 'max': 20, 'step': 1},
                'max_leaf_size': {'value': 20, 'type': 'slider', 'min': 10, 'max': 40, 'step': 1},
            },
            'graph': {
                'width': {'value': 30, 'type': 'slider', 'min': 10, 'max': 100, 'step': 1},
                'height': {'value': 30, 'type': 'slider', 'min': 10, 'max': 100, 'step': 1},
                'seed': {'value': None, 'type': 'input'},
                'max_rooms': {'value': 15, 'type': 'slider', 'min': 1, 'max': 50, 'step': 1},
                'min_room_size': {'value': 3, 'type': 'slider', 'min': 1, 'max': 10, 'step': 1},
                'max_room_size': {'value': 10, 'type': 'slider', 'min': 5, 'max': 20, 'step': 1},
            }
        }

        self.button_callbacks = {
            "Random": lambda : self.customize_menu(customize_menu_options['random']),
            "Perlin": lambda : self.customize_menu(customize_menu_options['perlin']),
            "Simplex": lambda : self.customize_menu(customize_menu_options['simplex']),
            "Cellular Automata": lambda : self.customize_menu(customize_menu_options['cellular']),
            "Binary Space Partitioning": lambda : self.customize_menu(customize_menu_options['bSP']),
            "Graph": lambda : self.customize_menu(customize_menu_options['graph']),
            "Back": self.go_back,
        }

        
        for idx, (label, callback) in enumerate(self.button_callbacks.items()):
            y_pos = initial_y + (button_height + button_margin) * idx
            self.buttons.append(Button(label, (x_pos, y_pos), (button_width, button_height), callback, self.font))
    
    def go_back(self):
        from game_states.menu import MenuScene
        self.game.scene_manager.go_to(MenuScene(self.game))
        
    def customize_menu(self, *options):
        self.game.scene_manager.go_to(CustomizeMenuScene(self.game, *options))

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


