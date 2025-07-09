# utils/slider.py

import pygame
from settings import BLACK, WHITE, GRAY

LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLUE = (50, 120, 230)

class Slider2:
    def __init__(self, display_name, pos, length, min_value, max_value, initial_value, callback, size=(14, 24), font=None, step=1.0):
        self.display_name = display_name
        self.pos = pos
        self.length = length
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.callback = callback
        self.dragging = False
        self.step = step

        self.handle_width = size[0]
        self.handle_height = size[1]
        self.rect = pygame.Rect(pos, (length, 8))  # thinner, stylized bar
        self.usable_width = length - self.handle_width

        self.font = font or pygame.font.SysFont("Arial", 20)
        self.small_font = pygame.font.SysFont("Arial", 14)

        self._update_handle_from_value()

    def _update_handle_from_value(self):
        relative_pos = (self.value - self.min_value) / (self.max_value - self.min_value)
        handle_x = self.rect.x + relative_pos * self.usable_width
        self.handle_rect = pygame.Rect(handle_x, self.rect.centery - self.handle_height // 2,
                                       self.handle_width, self.handle_height)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.handle_rect.collidepoint(mouse_pos)

        # Label on the left
        label_surface = self.font.render(self.display_name, True, BLACK)
        label_rect = label_surface.get_rect()
        label_rect.midright = (self.rect.x - 12, self.rect.centery)
        screen.blit(label_surface, label_rect)

        # Draw base slider bar
        pygame.draw.rect(screen, LIGHT_GRAY, self.rect, border_radius=4)

        # Draw progress fill
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, self.handle_rect.centerx - self.rect.x, self.rect.height)
        pygame.draw.rect(screen, BLUE, fill_rect, border_radius=4)

        # Draw the handle
        handle_color = BLUE if self.dragging or is_hovered else DARK_GRAY
        pygame.draw.ellipse(screen, handle_color, self.handle_rect)
        pygame.draw.ellipse(screen, BLACK, self.handle_rect, 2)

        # Format value with correct precision
        decimals = max(0, len(str(self.step).split('.')[-1])) if '.' in str(self.step) else 0
        value_text = f"{self.value:.{decimals}f}"

        # Draw min, max, and current value labels
        min_surf = self.small_font.render(f"{self.min_value:.{decimals}f}", True, DARK_GRAY)
        max_surf = self.small_font.render(f"{self.max_value:.{decimals}f}", True, DARK_GRAY)
        value_surf = self.small_font.render(value_text, True, BLACK)

        y_offset = 20
        screen.blit(min_surf, (self.rect.x, self.rect.bottom + y_offset))
        screen.blit(max_surf, (self.rect.right - max_surf.get_width(), self.rect.bottom + y_offset))
        value_rect = value_surf.get_rect(center=(self.rect.centerx, self.rect.bottom + y_offset))
        screen.blit(value_surf, value_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            new_x = max(self.rect.x, min(event.pos[0] - self.handle_width // 2, self.rect.right - self.handle_width))
            self.handle_rect.x = new_x

            relative_x = (new_x - self.rect.x) / self.usable_width
            raw_value = self.min_value + relative_x * (self.max_value - self.min_value)

            stepped_value = round(raw_value / self.step) * self.step
            stepped_value = max(self.min_value, min(stepped_value, self.max_value))

            if stepped_value != self.value:
                self.value = stepped_value
                self.callback(self.display_name, self.value)

    def get_value(self):
        return self.value
