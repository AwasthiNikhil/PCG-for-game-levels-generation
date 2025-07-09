import pygame
from core.base_scene import BaseScene
from utils.button import Button
from settings import WHITE, BLACK, GRAY
from settings import WIDTH, HEIGHT

class PauseScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("Arial", 24)
        print("game paused")
        self.buttons = [
            Button("Resume", (WIDTH/2 - 50, 200), (100, 40), self.resume, self.font),
            Button("Settings", (WIDTH/2 - 50, 270), (100, 40), self.go_back, self.font),
            Button("Main Menu", (WIDTH/2 - 50, 340), (100, 40), self.go_back, self.font)
        ]

    def resume(self):
        self.game.paused = False
        #  TODO: go back to game with state
        print("Resuming game...")
        from game_states.menu import MenuScene
        self.game.scene_manager.go_to(MenuScene(self.game))
        
    def go_back(self):
        self.game.paused = False
        print("Returning to main menu...")
        #  TODO: perform any necessary cleanup or state reset
        from game_states.menu import MenuScene
        self.game.scene_manager.go_to(MenuScene(self.game))

    def handle_events(self, events):
        for event in events:
            for button in self.buttons:
                button.handle_event(event)
            
    def update(self):
        pass

    def draw(self, screen):
        screen.fill(WHITE)

        # Draw button buttons
        for button in self.buttons:
            button.draw(screen)
