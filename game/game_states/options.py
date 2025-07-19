import pygame
from core.base_scene import BaseScene
from utils.button import Button
from settings import WHITE
from settings import WIDTH, HEIGHT
from utils.soundslider import SoundSlider
from utils.toggle import Toggle
from utils.controlbinding import ControlBinding
import random
import string

class OptionsScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("Arial", 24)
        self.active_tab = "Player"
        self.font2 = pygame.font.SysFont('Times New Roman', 30)
        

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
        
        self.profile_icon = pygame.image.load("assets/images/profile_icon/0.png")
        # self.player_name = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=5))
        self.player_name = self.game.settings['PLAYERNAME']

        self.customize_button = pygame.image.load("assets/images/icons/0.png")
        
        self.back_button = Button("Back", (WIDTH / 2 - 100, 480), (150, 50), self.go_back, self.font)

    def set_tab(self, tab_name):
        self.active_tab = tab_name

    def go_back(self):
        from game_states.menu import MenuScene
        self.game.scene_manager.go_to(MenuScene(self.game))

    def player_info(self, screen):
        screen.blit(self.profile_icon, (WIDTH/4, 150))
        name_text = self.font.render(self.player_name, True, (0, 0, 0))
        screen.blit(name_text, (WIDTH / 2 - WIDTH/4 + 100, 170))
        screen.blit(self.customize_button, (WIDTH - WIDTH/4, 150))
        
    def player_stats(self, screen):
        # player stats to be shown here
        pygame.draw.line(screen, (0, 0, 0), (WIDTH / 4, 250), (WIDTH* 4/5, 250), 2)
        
    def dev_mode(self, screen):
        self.dev_button = pygame.draw.rect(screen, (0, 0, 0), (WIDTH - 400, 270, 150, 50), 2)
        pygame.draw.rect(screen, (0, 0, 0), (WIDTH - 395, 275, 40, 40), 2)
        
        if self.game.mode == 'dev':
            tick = self.font2.render('O', True, (0, 0, 0))
            screen.blit(tick, (WIDTH - 385, 280))
        
        text = self.font.render('Dev', True, (0, 0, 0))
        screen.blit(text, (WIDTH - 340, 280))
        
        self.info_button = pygame.draw.circle(screen, (0, 0, 0), (WIDTH - 275, 295), 15, 2)
        question = self.font.render('?', True, (0, 0, 0))
        screen.blit(question, (WIDTH - 280, 280))
        
    def draw_player_tab(self, screen):
        self.player_info(screen)
        self.dev_mode(screen)
        self.player_stats(screen)

    def handle_events(self, events):
        for event in events:
            # Handle tab button events
            for tab in self.tabs:
                tab.handle_event(event)
            
            # Handle the active tab-specific events
            if self.active_tab == 'Player':
                if self.customize_button.get_rect(topleft=(WIDTH - WIDTH/4, 150)).collidepoint(pygame.mouse.get_pos()):
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        print("Customize button clicked")
                if self.dev_button.collidepoint(pygame.mouse.get_pos()):
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.game.mode = 'player' if self.game.mode =='dev' else 'dev'
                        print(self.game.mode)
            
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
            self.draw_player_tab(screen)
        elif self.active_tab == "Sound":
            for slider in self.sound_sliders:
                slider.draw(screen)
        elif self.active_tab == "Controls":
            for binding in self.control_bindings:
                binding.draw(screen)

        self.back_button.draw(screen)
