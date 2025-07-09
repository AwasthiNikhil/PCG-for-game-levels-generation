import pygame
from settings import WHITE, BLACK, GRAY

LIGHT_GRAY = (210, 210, 210)
DARK_GRAY = (100, 100, 100)
BLUE = (50, 120, 230)
PLACEHOLDER_COLOR = (150, 150, 150)

class InputField:
    def __init__(self, label, func, game, pos, size, font, input_type=str, max_len=30, placeholder="Write Something..."):
        self.label = label
        self.func = func
        self.game = game
        self.rect = pygame.Rect(pos, size)
        self.font = font
        self.input_type = input_type
        self.text = ""
        self.max_len = max_len
        self.placeholder = placeholder

        self.active = False
        self.cursor_pos = len(self.text)
        self.color_inactive = LIGHT_GRAY
        self.color_active = BLUE

        # Label rendered once
        self.label_surf = self.font.render(self.label, True, BLACK)
        self.label_rect = self.label_surf.get_rect()
        self.label_rect.midright = (self.rect.x - 12, self.rect.centery)

    def draw(self, screen):
        # Draw label to the left
        screen.blit(self.label_surf, self.label_rect)

        # Field color depending on focus
        bg_color = self.color_active if self.active else self.color_inactive
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=6)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=6)

        # Text rendering
        if not self.text and not self.active:
            text_surf = self.font.render(self.placeholder, True, PLACEHOLDER_COLOR)
        else:
            text_surf = self.font.render(self.text, True, BLACK)

        screen.blit(text_surf, (self.rect.x + 10, self.rect.y + (self.rect.height - text_surf.get_height()) // 2))

        # Draw blinking cursor if active
        if self.active and pygame.time.get_ticks() % 1000 < 500:
            text_offset = self.font.size(self.text[:self.cursor_pos])[0]
            cursor_x = self.rect.x + 10 + text_offset
            cursor_y1 = self.rect.y + 6
            cursor_y2 = self.rect.y + self.rect.height - 6
            pygame.draw.line(screen, BLACK, (cursor_x, cursor_y1), (cursor_x, cursor_y2), 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
                self.cursor_pos = len(self.text)
            else:
                if self.active:
                    self.func(self.label, self._get_validated_input())
                self.active = False

        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.func(self.label, self._get_validated_input())
            elif event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif event.key == pygame.K_RIGHT:
                self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
            else:
                if len(self.text) < self.max_len:
                    self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                    self.cursor_pos += 1

    def _get_validated_input(self):
        try:
            return self.input_type(self.text) if self.text else None
        except ValueError:
            return None
