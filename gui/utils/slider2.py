# utils/slider.py

import pygame
from settings import BLACK, WHITE, GRAY

class Slider2:
    def __init__(self, display_name, pos, length, min_value, max_value, initial_value, callback, size=(10, 20), font=None, step=1.0):
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
        self.rect = pygame.Rect(pos, (length, size[1]))
        self.usable_width = length - self.handle_width

        # Calculate handle position from initial value
        relative_pos = (initial_value - min_value) / (max_value - min_value)
        handle_x = pos[0] + relative_pos * self.usable_width
        self.handle_rect = pygame.Rect(handle_x, pos[1] - size[1] // 2, self.handle_width, self.handle_height)

        self.font = font or pygame.font.SysFont("Arial", 20)

    def draw(self, screen):
        # Draw label to the left of the slider
        label_surface = self.font.render(self.display_name, True, BLACK)
        label_rect = label_surface.get_rect()
        label_rect.midright = (self.rect.x - 10, self.rect.centery)
        screen.blit(label_surface, label_rect)

        # Draw the slider bar
        pygame.draw.rect(screen, GRAY, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

        # Draw the handle
        pygame.draw.rect(screen, BLACK, self.handle_rect)

        # Determine decimal places based on step
        decimals = max(0, len(str(self.step).split('.')[-1])) if '.' in str(self.step) else 0
        value_text = f"{self.value:.{decimals}f}"

        # Draw min, max, and current value labels below the slider
        min_surf = self.font.render(f"{self.min_value:.{decimals}f}", True, BLACK)
        max_surf = self.font.render(f"{self.max_value:.{decimals}f}", True, BLACK)
        value_surf = self.font.render(value_text, True, BLACK)

        y_offset = 25
        screen.blit(min_surf, (self.rect.x, self.rect.y + y_offset))
        screen.blit(max_surf, (self.rect.right - max_surf.get_width(), self.rect.y + y_offset))
        value_rect = value_surf.get_rect(center=(self.rect.centerx, self.rect.y + y_offset))
        screen.blit(value_surf, value_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                # Constrain within usable track (handle size considered)
                new_x = max(self.rect.x, min(event.pos[0] - self.handle_width // 2, self.rect.right - self.handle_width))
                self.handle_rect.x = new_x

                # Convert position to value
                relative_x = (new_x - self.rect.x) / self.usable_width
                raw_value = self.min_value + relative_x * (self.max_value - self.min_value)

                # Snap to nearest step
                stepped_value = round(raw_value / self.step) * self.step
                stepped_value = max(self.min_value, min(stepped_value, self.max_value))
                self.value = stepped_value
                self.callback(self.value)

    def get_value(self):
        return self.value
