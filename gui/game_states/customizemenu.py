import pygame
from core.base_scene import BaseScene
from utils.button import Button
from settings import WHITE
from settings import WIDTH, HEIGHT
from utils.slider import Slider

class CustomizeMenuScene(BaseScene):
    def __init__(self, game, *menu_options):
        super().__init__(game)
        self.font = pygame.font.SysFont("Arial", 24)
        
        self.menu_options = menu_options 
        print(*self.menu_options)
        
        # Sound button sliders configuration
        self.sound_sliders_config = [
            ("Master Volume", 'MASTER_VOL', game, 0.0, 1.0, 0.01, (WIDTH / 2 - 100, 180)),
        ]

        # Dynamically create sliders for sound settings
        self.sound_sliders = [
            Slider(label, setting_key, game, min_val, max_val, step, pos, self.font)
            for label, setting_key, game, min_val, max_val, step, pos in self.sound_sliders_config
        ]

        # Back button configuration (static in this case)
        self.back_button = Button("Back", (WIDTH / 2 - 100, 480), (150, 50), self.go_back, self.font)


    def go_back(self):
        from game_states.gametype import SelectGameTypeScene        
        self.game.scene_manager.go_to(SelectGameTypeScene(self.game))

    def handle_events(self, events):
        for event in events:
            self.back_button.handle_event(event)

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(WHITE)
        
        for slider in self.sound_sliders:
            slider.draw(screen)

        # Draw back button
        self.back_button.draw(screen)
