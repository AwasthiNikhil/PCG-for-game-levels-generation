import pygame
from core.base_scene import BaseScene
from utils.button import Button
from settings import WHITE, BLACK, GRAY
from settings import WIDTH, HEIGHT

class Slider:
    def __init__(self, label, key, game, min_val, max_val, step, pos, font):
        self.label = label
        self.key = key
        self.game = game
        self.min = min_val
        self.max = max_val
        self.step = step
        self.pos = pos
        self.width = 200
        self.height = 10
        self.font = font
        self.slider_rect = pygame.Rect(pos[0], pos[1], self.width, self.height)

    def get_value(self):
        return self.game.settings[self.key]

    def draw(self, screen):
        val = self.get_value()
        percent = (val - self.min) / (self.max - self.min)
        handle_x = self.slider_rect.x + percent * self.slider_rect.width

        pygame.draw.rect(screen, GRAY, self.slider_rect)
        pygame.draw.circle(screen, BLACK, (int(handle_x), self.slider_rect.centery), 8)

        label_surf = self.font.render(f"{self.label}: {val:.2f}", True, BLACK)
        screen.blit(label_surf, (self.slider_rect.x, self.slider_rect.y - 25))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.slider_rect.collidepoint(event.pos):
            self._set_value_from_pos(event.pos[0])
        elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
            if self.slider_rect.collidepoint(event.pos):
                self._set_value_from_pos(event.pos[0])

    def _set_value_from_pos(self, x_pos):
        rel_x = x_pos - self.slider_rect.x
        percent = max(0, min(1, rel_x / self.slider_rect.width))
        value = self.min + percent * (self.max - self.min)
        stepped_value = round(value / self.step) * self.step
        self.game.settings[self.key] = max(self.min, min(self.max, stepped_value))

class Toggle:
    def __init__(self, label, key, game, pos, font):
        self.label = label
        self.key = key
        self.game = game
        self.rect = pygame.Rect(pos[0], pos[1], 120, 30)
        self.font = font

    def draw(self, screen):
        val = self.game.settings.get(self.key, False)
        text = f"{self.label}: {'ON' if val else 'OFF'}"
        text_surf = self.font.render(text, True, BLACK)
        pygame.draw.rect(screen, GRAY if val else WHITE, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        screen.blit(text_surf, self.rect.move(10, 5))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            current = self.game.settings.get(self.key, False)
            self.game.settings[self.key] = not current

class ControlBinding:
    def __init__(self, label, action, game, pos, font):
        self.label = label
        self.action = action
        self.game = game
        self.pos = pos
        self.font = font
        self.rect = pygame.Rect(pos[0], pos[1], 300, 40)
        self.listening = False

    def draw(self, screen):
        # Draw background and border
        color = (180, 180, 255) if self.listening else WHITE
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

        # Draw action label
        label_surf = self.font.render(self.label, True, BLACK)
        screen.blit(label_surf, (self.rect.x + 10, self.rect.y + 8))

        # Draw current key name
        key_val = self.game.settings['CONTROLS'].get(self.action, None)
        key_name = pygame.key.name(key_val) if key_val else "Unbound"
        key_surf = self.font.render(key_name, True, BLACK)
        screen.blit(key_surf, (self.rect.right - key_surf.get_width() - 10, self.rect.y + 8))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.listening = True
        elif event.type == pygame.KEYDOWN and self.listening:
            # Update key binding
            self.game.settings['CONTROLS'][self.action] = event.key
            self.listening = False

class OptionsScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("Arial", 24)
        self.active_tab = "Video"

        self.tabs = [
            Button("Video", (430, 100), (100, 40), lambda: self.set_tab("Video"), self.font),
            Button("Sound", (550, 100), (100, 40), lambda: self.set_tab("Sound"), self.font),
            Button("Controls", (670, 100), (120, 40), lambda: self.set_tab("Controls"), self.font)
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

            if self.active_tab == "Video":
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

        if self.active_tab == "Video":
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
