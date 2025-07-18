import pygame
from core.base_scene import BaseScene
from utils.button import Button
from settings import WHITE, BLACK, GRAY
from settings import WIDTH, HEIGHT
from utils.inputfield import InputField  # Import the InputField class

class RegisterScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("Arial", 24)
        self.title_font = pygame.font.SysFont("Arial", 32)
        
        # Create input fields for username and password using InputField
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

        # Buttons
        self.buttons = [
            Button("Register", (WIDTH / 2 - 50, 350), (100, 40), self.register, self.font),
        ]

    def on_input_change(self, field_label, value):
        """Callback for input change to handle updates."""
        if field_label == "Username":
            self.username_input = value
        elif field_label == "Password":
            self.password_input = value
        print(f"{field_label}: {value}")

    def register(self):
        print("hi")
        # Process the registration here
        # print(f"Registering {self.username_input} with password {self.password_input}")
        
        # # For now, just print and go to menu scene
        # from game_states.menu import MenuScene
        # self.game.scene_manager.go_to(MenuScene(self.game))

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
        screen.blit(title_text, (WIDTH/2 - title_text.get_width()/2, 50))

        # Draw input fields
        self.username_input_field.draw(screen)
        self.password_input_field.draw(screen)

        # Draw buttons
        for button in self.buttons:
            button.draw(screen)
