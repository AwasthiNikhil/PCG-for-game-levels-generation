import pygame
from core.base_scene import BaseScene
from utils.button import Button
from settings import WHITE
from settings import WIDTH, HEIGHT
from utils.slider import Slider
from utils.toggle import Toggle
from utils.controlbinding import ControlBinding

class OptionsScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("Arial", 24)
        self.active_tab = "Player"

        self.tabs = [
            Button("Player", (430, 100), (100, 40), lambda: self.set_tab("Player"), self.font),
            Button("Video", (550, 100), (100, 40), lambda: self.set_tab("Video"), self.font),
            Button("Sound", (670, 100), (120, 40), lambda: self.set_tab("Sound"), self.font),
            Button("Controls", (800, 100), (120, 40), lambda: self.set_tab("Controls"), self.font)
        ]

        # Video tab sliders & toggles
        self.video_sliders = [
            Slider("WIDTH", 'WIDTH', game, 10, 40, 1, (WIDTH/2 - 100, 180), self.font),
            Slider("HEIGHT", 'HEIGHT', game, 10, 40, 1, (WIDTH/2 - 100, 240), self.font),
            Slider("SCALE", 'SCALE', game, 0.5, 4.0, 0.1, (WIDTH/2 - 100, 300), self.font)
        ]
        self.video_toggles = [
            Toggle("Fullscreen", 'FULLSCREEN', game, (WIDTH/2 - 100, 360), self.font),
            Toggle("V-Sync", 'VSYNC', game, (WIDTH/2 - 100, 410), self.font)
        ]

        # Sound tab sliders
        self.sound_sliders = [
            Slider("Master Volume", 'MASTER_VOL', game, 0.0, 1.0, 0.01, (WIDTH/2 - 100, 180), self.font),
            Slider("Music Volume", 'MUSIC_VOL', game, 0.0, 1.0, 0.01, (WIDTH/2 - 100, 240), self.font),
            Slider("SFX Volume", 'SFX_VOL', game, 0.0, 1.0, 0.01, (WIDTH/2 - 100, 300), self.font)
        ]
        # Controls bindings
        if 'CONTROLS' not in self.game.settings:
            self.game.settings['CONTROLS'] = {
                'MOVE_LEFT': pygame.K_LEFT,
                'MOVE_RIGHT': pygame.K_RIGHT,
                'JUMP': pygame.K_SPACE,
                'SHOOT': pygame.K_z,
            }

        self.control_bindings = [
            ControlBinding("Move Left", 'MOVE_LEFT', game, (WIDTH/2 - 150, 180), self.font),
            ControlBinding("Move Right", 'MOVE_RIGHT', game, (WIDTH/2 - 150, 230), self.font),
            ControlBinding("Jump", 'JUMP', game, (WIDTH/2 - 150, 280), self.font),
            ControlBinding("Shoot", 'SHOOT', game, (WIDTH/2 - 150, 330), self.font),
        ]

        self.back_button = Button("Back", (WIDTH/2 - 100, 480), (150, 50), self.go_back, self.font)

    def set_tab(self, tab_name):
        self.active_tab = tab_name

    def go_back(self):
        from game_states.menu import MenuScene
        self.game.scene_manager.go_to(MenuScene(self.game))

    def handle_events(self, events):
        for event in events:
            for tab in self.tabs:
                tab.handle_event(event)

            if self.active_tab == 'Player':
                # TODO: Handle player-specific options here if needed
                pass
            elif self.active_tab == "Video":
                for slider in self.video_sliders:
                    slider.handle_event(event)
                for toggle in self.video_toggles:
                    toggle.handle_event(event)
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

        if self.active_tab == "Player":
            pass
        elif self.active_tab == "Video":
            for slider in self.video_sliders:
                slider.draw(screen)
            for toggle in self.video_toggles:
                toggle.draw(screen)
        elif self.active_tab == "Sound":
            for slider in self.sound_sliders:
                slider.draw(screen)
        elif self.active_tab == "Controls":
            for binding in self.control_bindings:
                binding.draw(screen)

        # Back button
        self.back_button.draw(screen)
