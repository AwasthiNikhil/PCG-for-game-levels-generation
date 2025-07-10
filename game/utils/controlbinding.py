import pygame
from settings import WHITE, BLACK

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
        # key_val = self.game.settings['CONTROLS'].get(self.action, None)
        controls = self.game.settings_manager.get_setting('CONTROLS', {}) 
        key_val = controls.get(self.action, None)  
        key_name = pygame.key.name(key_val) if key_val else "Unbound"
        key_surf = self.font.render(key_name, True, BLACK)
        screen.blit(key_surf, (self.rect.right - key_surf.get_width() - 10, self.rect.y + 8))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.listening = True
        elif event.type == pygame.KEYDOWN and self.listening:
            # Update key binding
            # self.game.settings['CONTROLS'][self.action] = event.key
            controls = self.game.settings_manager.get_setting('CONTROLS', {})
            controls[self.action] = event.key
            self.game.settings_manager.set_setting('CONTROLS', controls)
            self.listening = False
            
