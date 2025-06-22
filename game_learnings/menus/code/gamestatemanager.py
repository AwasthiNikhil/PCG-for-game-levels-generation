from settings import *
from button import Button

# Game state manager
class GameStateManager:
    def __init__(self, screen):
        self.screen = screen
        self.state_stack = ["main_menu"]

    def push_state(self, state):
        self.state_stack.append(state)

    def pop_state(self):
        if len(self.state_stack) > 1:
            self.state_stack.pop()

    def current_state(self):
        return self.state_stack[-1]

    def handle_menu_navigation(self, buttons, event, selected_index):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP):  # Navigate up
                selected_index[0] = (selected_index[0] - 1) % len(buttons)
            elif event.key in (pygame.K_s, pygame.K_DOWN):  # Navigate down
                selected_index[0] = (selected_index[0] + 1) % len(buttons)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):  # Select button
                buttons[selected_index[0]].on_click()
            elif event.key == pygame.K_ESCAPE:  # Go back
                self.pop_state()

    def main_menu(self):
        buttons = [
            Button("Play", SCREEN_WIDTH // 2 - 100, 200, BUTTON_WIDTH, BUTTON_HEIGHT, lambda: self.push_state("generation_menu")),
            Button("Options", SCREEN_WIDTH // 2 - 100, 300, BUTTON_WIDTH, BUTTON_HEIGHT, lambda: self.push_state("options")),
            Button("Exit", SCREEN_WIDTH // 2 - 100, 400, BUTTON_WIDTH, BUTTON_HEIGHT, lambda: sys.exit())
        ]
        selected_index = [0]

        running = True
        while running and self.current_state() == "main_menu":
            self.screen.fill(WHITE)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.handle_menu_navigation(buttons, event, selected_index)
                for button in buttons:
                    button.handle_event(event)

            for i, button in enumerate(buttons):
                button.draw(self.screen, highlight=(i == selected_index[0]))

            pygame.display.flip()
            pygame.time.Clock().tick(FPS)

    def play(self):
        running = True
        while running and self.current_state() == "play":
            self.screen.fill(WHITE)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.pop_state()

            # Placeholder for game logic
            font = pygame.font.Font(None, 36)
            text_surface = font.render("Game Playing... Press ESC to return", True, BLACK)
            self.screen.blit(text_surface, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2))

            pygame.display.flip()
            pygame.time.Clock().tick(FPS)

    def options(self):
        running = True
        while running and self.current_state() == "options":
            self.screen.fill(WHITE)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.pop_state()

            # Placeholder for options logic
            font = pygame.font.Font(None, 36)
            text_surface = font.render("Options Menu... Press ESC to return", True, BLACK)
            self.screen.blit(text_surface, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2))

            pygame.display.flip()
            pygame.time.Clock().tick(FPS)

    def generation_menu(self):
        buttons = [
            Button("Random Generation", SCREEN_WIDTH // 2 - 150, 100, BUTTON_WIDTH_L, 50, lambda: self.push_state("play")),
            Button("Perlin", SCREEN_WIDTH // 2 - 150, 160, BUTTON_WIDTH_L, 50, lambda: self.push_state("play")),
            Button("Simplex", SCREEN_WIDTH // 2 - 150, 220, BUTTON_WIDTH_L, 50, lambda: self.push_state("play")),
            Button("Cellular Automata", SCREEN_WIDTH // 2 - 150, 280, BUTTON_WIDTH_L, 50, lambda: self.push_state("play")),
            Button("Binary Space Partitioning (BSP)", SCREEN_WIDTH // 2 - 150, 340, BUTTON_WIDTH_L, 50, lambda: self.push_state("play")),
            Button("Wave Function Collapse (WFC)", SCREEN_WIDTH // 2 - 150, 400, BUTTON_WIDTH_L, 50, lambda: self.push_state("play")),
            Button("Graph-Based Generation", SCREEN_WIDTH // 2 - 150, 460, BUTTON_WIDTH_L, 50, lambda: self.push_state("play")),
            Button("Back", SCREEN_WIDTH // 2 - 150, 520, BUTTON_WIDTH_L, 50, lambda: self.pop_state())
        ]
        selected_index = [0]

        running = True
        while running and self.current_state() == "generation_menu":
            self.screen.fill(WHITE)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.handle_menu_navigation(buttons, event, selected_index)
                for button in buttons:
                    button.handle_event(event)

            for i, button in enumerate(buttons):
                button.draw(self.screen, highlight=(i == selected_index[0]))

            pygame.display.flip()
            pygame.time.Clock().tick(FPS)

    def run(self):
        while True:
            current = self.current_state()
            if current == "main_menu":
                self.main_menu()
            elif current == "play":
                self.play()
            elif current == "options":
                self.options()
            elif current == "generation_menu":
                self.generation_menu()
