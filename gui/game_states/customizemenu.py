import pygame
from core.base_scene import BaseScene
from utils.button import Button
from settings import WHITE
from settings import WIDTH, HEIGHT
from utils.slider import Slider
from utils.slider2 import Slider2
from utils.inputfield import InputField

class CustomizeMenuScene(BaseScene):
    def __init__(self, game, *menu_options):
        super().__init__(game)
        self.font = pygame.font.SysFont("Arial", 24)
        
        self.menu = []


        for menu_items in menu_options:
            for i, menu_item in enumerate(menu_items):
                if menu_items[menu_item]['type'] == 'slider':
                    self.menu.append(
                        Slider2(
                            display_name= menu_item,
                            pos=(WIDTH/2 - 100,100 + i * 60), 
                            length= 400, 
                            min_value= menu_items[menu_item]['min'], 
                            max_value= menu_items[menu_item]['max'], 
                            initial_value= menu_items[menu_item]['value'], 
                            callback=self.on_slider_change
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
        
        self.back_button = Button("Back", (WIDTH / 2 - 100, 480), (150, 50), self.go_back, self.font)

    def on_slider_change(self, value):
        print(f"Value: {value:.2f}")

    def on_input_change(self, text):
        # self.text = text
        pass
        # print(f"Text set to: {self.text}")

    def go_back(self):
        from game_states.gametype import SelectGameTypeScene        
        self.game.scene_manager.go_to(SelectGameTypeScene(self.game))

    def handle_events(self, events):
        for event in events:
            for menu in self.menu:
                menu.handle_event(event)
            self.back_button.handle_event(event)

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(WHITE)
        
        for menu in self.menu:
            menu.draw(screen)

        self.back_button.draw(screen)
