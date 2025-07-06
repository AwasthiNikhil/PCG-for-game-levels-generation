# utils/slider.py

import pygame
from settings import BLACK, WHITE, GRAY

class Slider2:
    def __init__(self, pos, length, min_value, max_value, initial_value, callback, size=(10, 20)):
        self.rect = pygame.Rect(pos, (length, size[1]))
        self.handle_rect = pygame.Rect(pos[0] + (initial_value - min_value) / (max_value - min_value) * length - size[0] // 2,
                                       pos[1] - size[1] // 2, size[0], size[1])
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.callback = callback
        self.dragging = False
        self.handle_width = size[0]
        self.handle_height = size[1]

    def draw(self, screen):
        # Draw the slider bar
        pygame.draw.rect(screen, GRAY, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

        # Draw the handle
        pygame.draw.rect(screen, BLACK, self.handle_rect)

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
