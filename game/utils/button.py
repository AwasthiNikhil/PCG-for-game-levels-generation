# utils/button.py

import pygame
from settings import BLACK, WHITE, GRAY

class Button:
    def __init__(self, text, pos, size, callback, font=None):
        self.text = text
        self.rect = pygame.Rect(pos, size)
        self.callback = callback
        self.font = font or pygame.font.SysFont("Arial", 30)
        self.hovered = False

    def draw(self, screen):
        color = GRAY if self.hovered else WHITE
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered:
                self.callback()
