import pygame
from settings import WHITE, BLACK, GRAY

class InputField:
    def __init__(self, label, func, game, pos, size, font, input_type=str, max_len=30, placeholder="Enter text..."):
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
        self.color_inactive = GRAY
        self.color_active = (127, 127, 127)

        # Label surface and rect
        self.label_surf = self.font.render(self.label, True, BLACK)
        self.label_rect = self.label_surf.get_rect()
        self.label_rect.midright = (self.rect.x - 10, self.rect.centery)

    def draw(self, screen):
        # Draw label to the left of input field
        screen.blit(self.label_surf, self.label_rect)

        # Draw the input field rectangle
        color = self.color_active if self.active else self.color_inactive
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

        # Draw placeholder or actual text
        if not self.text and not self.active:
            text_surf = self.font.render(self.placeholder, True, BLACK)
        else:
            text_surf = self.font.render(self.text, True, BLACK)
        
        screen.blit(text_surf, (self.rect.x + 10, self.rect.y + 10))

        # Draw the cursor
        if self.active and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = self.rect.x + 10 + self.font.size(self.text[:self.cursor_pos])[0]
            pygame.draw.line(screen, BLACK, (cursor_x, self.rect.y + 10), (cursor_x, self.rect.y + self.rect.height - 10), 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicks inside the input field, toggle the active state
            if self.rect.collidepoint(event.pos):
                self.active = True
                self.cursor_pos = len(self.text)
            else:
                if self.active:
                    self.func(self._get_validated_input())
                self.active = False

        elif event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.func(self._get_validated_input())
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:max(0, self.cursor_pos - 1)] + self.text[self.cursor_pos:]
                    self.cursor_pos = max(0, self.cursor_pos - 1)
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
