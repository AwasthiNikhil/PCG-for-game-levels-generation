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
        self.color_active = (127,127,127)

    def draw(self, screen):
        # Draw label
        label_surf = self.font.render(self.label, True, BLACK)
        screen.blit(label_surf, (self.rect.x, self.rect.y - 25))
        
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
                self.cursor_pos = len(self.text)  # Reset cursor position to the end
            else:
                self.active = False
                self.func(self._get_validated_input())

        elif event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    # Enter key pressed, store the value
                    self.func(self._get_validated_input())
                elif event.key == pygame.K_BACKSPACE:
                    # Backspace key pressed, remove last character
                    self.text = self.text[:-1]
                elif event.key == pygame.K_TAB:
                    # Tab key, just move the cursor one position forward
                    self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
                else:
                    # Any other key, add the character to the text
                    if len(self.text) < self.max_len:  # Limit input length to avoid overflow
                        self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                        self.cursor_pos += 1

    def _get_validated_input(self):
        """Validate and return the input, ensuring it's the correct type."""
        try:
            return self.input_type(self.text) if self.text else None
        except ValueError:
            return None  # Return None or a default value if the conversion fails
