import pygame
from settings import BLACK, GRAY
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

        label_surf = self.font.render(f"{self.label}: {int(val*100)}", True, BLACK)
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
