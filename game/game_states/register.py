import pygame
from core.base_scene import BaseScene
from utils.button import Button
from settings import WHITE, BLACK, RED
from settings import WIDTH, HEIGHT
from utils.inputfield import InputField

class RegisterScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("Arial", 24)
        self.title_font = pygame.font.SysFont("Arial", 32)
        self.error_font = pygame.font.SysFont("Arial", 20)

        self.username_input = ""
        self.password_input = ""

        self.username_input_field = InputField(
            "Username", self.on_input_change, game,
            (WIDTH/2 - 100, 150), (400, 40), pygame.font.SysFont("Arial", 30),
            placeholder="Enter Username"
        )
        self.password_input_field = InputField(
            "Password", self.on_input_change, game,
            (WIDTH/2 - 100, 250), (400, 40), pygame.font.SysFont("Arial", 30),
            input_type=str, placeholder="Enter Password"
        )

        self.buttons = [
            Button("Let's Goo!", (WIDTH / 2 - 50, 350), (100, 40), self.register, self.font),
        ]
        
        self.error_message = ''  # Displayed if login/register fails

    def on_input_change(self, field_label, value):
        if field_label == "Username":
            self.username_input = value
        elif field_label == "Password":
            self.password_input = value
        print(f"{field_label}: {value}")

    def register(self):
        # Reset error message
        self.error_message = ''

        if not self.username_input or not self.password_input:
            self.error_message = "Username and password cannot be empty."
            return

        try:
            success, result = self.game.network_manager.login_or_register_user(
                self.username_input.strip(), self.password_input.strip()
            )

            if success:
                user = result
                self.game.settings['USERID'] = user[0]
                self.game.settings['PLAYERNAME'] = user[1]
                self.game.settings_manager.save_settings(self.game.settings)

                from game_states.menu import MenuScene
                self.game.scene_manager.go_to(MenuScene(self.game))
            else:
                self.error_message = str(result)  # e.g., "Incorrect password"
        except Exception as e:
            print(f"Unexpected error: {e}")
            self.error_message = "Server error. Please try again later."

    def go_back(self):
        print("Returning to main menu...")
        from game_states.menu import MenuScene
        self.game.scene_manager.go_to(MenuScene(self.game))

    def handle_events(self, events):
        for event in events:
            for button in self.buttons:
                button.handle_event(event)

            self.username_input_field.handle_event(event)
            self.password_input_field.handle_event(event)

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(WHITE)

        # Draw title
        title_text = self.title_font.render("Register Account", True, BLACK)
        screen.blit(title_text, (WIDTH / 2 - title_text.get_width() / 2, 50))

        # Draw input fields
        self.username_input_field.draw(screen)
        self.password_input_field.draw(screen)

        # Draw buttons
        for button in self.buttons:
            button.draw(screen)

        # Draw error message (if any)
        if self.error_message:
            error_surf = self.error_font.render(self.error_message, True, RED)
            screen.blit(error_surf, (WIDTH / 2 - error_surf.get_width() / 2, 420))
