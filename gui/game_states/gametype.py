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
                'width' : {'value': 30, 'type': 'input'},
                'height' : {'value': 30, 'type': 'input'},
                'seed' : {'value': None, 'type': 'input'},
                'wall_probability' : {'value': 0.2, 'type': 'input'},
            },
            'perlin': {
                'width' : 30,
                'height' : 30,
                'seed' : None,
                'scale' : 2,
                'threshold' : 0,
                'min_room_size' : 4,
            },
            'simplex': {
                'width' : 30,
                'height' : 30,
                'seed' : None,
                'scale' : 2,
                'threshold' : 0,
            },
            'cellular': {
                'width' : 30,
                'height' : 30,
                'seed' : None,
                'wall_probability' : 0.55,
                'iterations' : 1
            },
            'bSP': {
                'width' : 30,
                'height' : 30,
                'seed' : None,
                'min_leaf_size' : 6,
                'max_leaf_size' : 20,
            },
            'graph': {
                'width' : 30,
                'height' : 30,
                'seed' : None,
                'max_rooms' : 15,
                'min_room_size' : 3,
                'max_room_size' : 10,
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


