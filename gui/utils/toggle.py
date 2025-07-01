import pygame
from settings import WHITE, BLACK, GRAY
class Toggle:
    def __init__(self, label, key, game, pos, font):
        self.label = label
        self.key = key
        self.game = game
        self.rect = pygame.Rect(pos[0], pos[1], 200, 40)
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
