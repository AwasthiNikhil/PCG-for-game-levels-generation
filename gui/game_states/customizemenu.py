import pygame
from core.base_scene import BaseScene
from utils.button import Button
from settings import WHITE
from settings import WIDTH, HEIGHT
from utils.slider import Slider
from utils.slider2 import Slider2
from utils.inputfield import InputField

class CustomizeMenuScene(BaseScene):
    def __init__(self, game, level_type, *menu_options):
        super().__init__(game)
        self.font = pygame.font.SysFont("Arial", 24)
        self.menu = [] # menu items
        self.data = {'type': level_type} # level data to pass to the next scene

        for menu_items in menu_options:
            for i, menu_item in enumerate(menu_items):
                if menu_items[menu_item]['type'] == 'slider':
                    self.menu.append(
                        Slider2(
                            display_name= menu_item,
                            pos= (WIDTH/2 - 100,100 + i * 60), 
                            length=  400, 
                            min_value=  menu_items[menu_item]['min'], 
                            max_value=  menu_items[menu_item]['max'], 
                            initial_value=  menu_items[menu_item]['value'], 
                            callback= self.on_slider_change,
                        )
                    )
                elif menu_items[menu_item]['type'] == 'input':
                    self.menu.append(
                        InputField(
                            menu_item,
                            self.on_input_change,
                            game,
                            (WIDTH/2 - 100,100 + i * 60),
                            (400, 40),
                            pygame.font.SysFont("Arial", 30)
                        )
                    )
                self.data[menu_item] = menu_items[menu_item]['value']
        
        self.play_button = Button("Play", (WIDTH / 2 - 100, 480), (150, 50), self.play, self.font)
        self.back_button = Button("Back", (WIDTH / 2 - 100, 550), (150, 50), self.go_back, self.font)

    def on_slider_change(self, menu_item, value):
        print(f"{menu_item}: {value:.2f}")

    def on_input_change(self, menu_item, value):
        print(f"{menu_item}: {value}")

    def go_back(self):
        from game_states.gametype import SelectGameTypeScene        
        self.game.scene_manager.go_to(SelectGameTypeScene(self.game))
        
    def play(self):
        from game_states.loadgame import LoadGame        
        self.game.scene_manager.go_to(LoadGame(self.game, self.data))

    def handle_events(self, events):
        for event in events:
            for menu in self.menu:
                menu.handle_event(event)
            self.play_button.handle_event(event)
            self.back_button.handle_event(event)

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(WHITE)
        
        for menu in self.menu:
            menu.draw(screen)

        self.play_button.draw(screen)
        self.back_button.draw(screen)
