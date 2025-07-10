import pygame
from core.base_scene import BaseScene
from utils.button import Button
from settings import WHITE
from settings import WIDTH, HEIGHT
from utils.soundslider import SoundSlider
from utils.toggle import Toggle
from utils.controlbinding import ControlBinding

class OptionsScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("Arial", 24)
        self.active_tab = "Player"

        self.tabs_config = {
            "Player": lambda: self.set_tab("Player"),
            "Sound": lambda: self.set_tab("Sound"),
            "Controls": lambda: self.set_tab("Controls")
        }

        self.tabs = [Button(name, (430 + i * 120, 100), (100, 40), callback, self.font)
                     for i, (name, callback) in enumerate(self.tabs_config.items())]

        
        self.sound_sliders_config = [
            ("Master Volume", 'MASTER_VOL', game, 0.0, 1.0, 0.01, (WIDTH / 2 - 100, 180)),
            ("Music Volume", 'MUSIC_VOL', game, 0.0, 1.0, 0.01, (WIDTH / 2 - 100, 240)),
            ("SFX Volume", 'SFX_VOL', game, 0.0, 1.0, 0.01, (WIDTH / 2 - 100, 300))
        ]

        self.sound_sliders = [
            SoundSlider(label, setting_key, game, min_val, max_val, step, pos, self.font)
            for label, setting_key, game, min_val, max_val, step, pos in self.sound_sliders_config
        ]


        if not self.game.settings_manager.get_setting('CONTROLS'): 
            self.game.settings_manager.set_setting('CONTROLS', {   
                'MOVE_LEFT': pygame.K_LEFT,
                'MOVE_RIGHT': pygame.K_RIGHT,
                'JUMP': pygame.K_SPACE,
                'SHOOT': pygame.K_z,
            })

        self.control_bindings_config = [
            ("Move Left", 'MOVE_LEFT', game, (WIDTH / 2 - 150, 180)),
            ("Move Right", 'MOVE_RIGHT', game, (WIDTH / 2 - 150, 230)),
            ("Jump", 'JUMP', game, (WIDTH / 2 - 150, 280)),
            ("Shoot", 'SHOOT', game, (WIDTH / 2 - 150, 330))
        ]

        self.control_bindings = [
            ControlBinding(action, control, game, pos, self.font)
            for action, control, game, pos in self.control_bindings_config
        ]

        self.back_button = Button("Back", (WIDTH / 2 - 100, 480), (150, 50), self.go_back, self.font)

    def set_tab(self, tab_name):
        self.active_tab = tab_name

    def go_back(self):
        from game_states.menu import MenuScene
        self.game.scene_manager.go_to(MenuScene(self.game))

    def handle_events(self, events):
        for event in events:
            # Handle tab button events
            for tab in self.tabs:
                tab.handle_event(event)

            # Handle the active tab-specific events
            if self.active_tab == 'Player':
                # TODO: Handle player-specific options here if needed
                pass
            elif self.active_tab == "Sound":
                for slider in self.sound_sliders:
                    slider.handle_event(event)
            elif self.active_tab == "Controls":
                for binding in self.control_bindings:
                    binding.handle_event(event)

            self.back_button.handle_event(event)

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(WHITE)

        # Draw tab buttons
        for tab in self.tabs:
            tab.draw(screen)

        # Draw the active tab's content
        if self.active_tab == "Player":
            pass
        elif self.active_tab == "Sound":
            for slider in self.sound_sliders:
                slider.draw(screen)
        elif self.active_tab == "Controls":
            for binding in self.control_bindings:
                binding.draw(screen)

        self.back_button.draw(screen)
