# utils/slider.py

import pygame
from settings import BLACK, WHITE, GRAY

class Slider2:
    def __init__(self, display_name, pos, length, min_value, max_value, initial_value, callback, size=(10, 20), font=None):
        self.display_name = display_name
        self.pos = pos
        self.length = length
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.callback = callback
        self.dragging = False

        self.handle_width = size[0]
        self.handle_height = size[1]
        self.rect = pygame.Rect(pos, (length, size[1]))
        self.handle_rect = pygame.Rect(
            pos[0] + (initial_value - min_value) / (max_value - min_value) * length - size[0] // 2,
            pos[1] - size[1] // 2,
            size[0], size[1]
        )

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

        # Draw min, max, and current value labels below the slider
        min_surf = self.font.render(str(int(self.min_value)), True, BLACK)
        max_surf = self.font.render(str(int(self.max_value)), True, BLACK)
        value_surf = self.font.render(f"{int(self.value)}", True, BLACK)

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
                # Calculate the new position of the handle based on the mouse movement
                new_x = max(self.rect.x, min(event.pos[0] - self.handle_width // 2, self.rect.x + self.rect.width - self.handle_width))
                self.handle_rect.x = new_x
                self.value = self.min_value + ((new_x - self.rect.x) / self.rect.width) * (self.max_value - self.min_value)
                self.callback(self.value)  # Call the callback with the new value

    def get_value(self):
        return self.value
