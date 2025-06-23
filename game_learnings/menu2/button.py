from settings import *
import pygame
pygame.init()  # Initialize Pygame, including the font module

# Button class
class Button:
    def __init__(self, text, x, y, width = BUTTON_WIDTH, height = BUTTON_HEIGHT):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(None, 16)
        self.color = GRAY

    def draw(self, screen, highlight=False):
        color = 'LIGHT BLUE' if highlight else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

# Image loading example
try:
    image = pygame.image.load('path/to/image.png')  # Replace with your image path
except pygame.error as e:
    print(f"Unable to load image: {e}")
    raise
