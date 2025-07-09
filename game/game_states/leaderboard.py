import pygame
from core.base_scene import BaseScene
from utils.button import Button
from settings import WHITE, BLACK
from settings import WIDTH, HEIGHT

class Leaderboard(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("Arial", 24)
        self.buttons = []

        # Back button configuration
        self.back_button = Button("Back", (WIDTH / 2 - 100, HEIGHT - 50), (80, 40), self.go_back, self.font)        
        self.buttons.append(self.back_button)

        # Static leaderboard data (will later be fetched from a database or file)
        self.leaderboard_data = [
            {'rank': 1, 'name': "PlayerOne", 'level_type': "Random", 'seed': 12345, 'date': '2023-06-25', 'score': 1200},
            {'rank': 2, 'name': "PlayerTwo", 'level_type': "BSP", 'seed': 67890, 'date': '2023-06-26', 'score': 1100},
            {'rank': 3, 'name': "PlayerThree", 'level_type': "Random", 'seed': 13579, 'date': '2023-06-27', 'score': 1050},
            {'rank': 4, 'name': "PlayerFour", 'level_type': "Perlin", 'seed': 24680, 'date': '2023-06-28', 'score': 950},
            {'rank': 5, 'name': "PlayerFive", 'level_type': "Random", 'seed': 11223, 'date': '2023-06-29', 'score': 900}
        ]

        # UI Layout Constants
        self.x_pos = WIDTH/2 - 300
        self.y_pos = 100
        self.line_height = 70  # Space between leaderboard lines

        # Title and header for the leaderboard
        self.title = self.font.render("Leaderboard", True, BLACK)  # White title
        self.header = self.font.render("Rank  Name        Level  Seed   Date       Score", True, BLACK)

        # Generate leaderboard display data
        self.data = self.create_leaderboard_data()

    def go_back(self):
        from game_states.menu import MenuScene
        self.game.scene_manager.go_to(MenuScene(self.game))

    def create_leaderboard_data(self):
        """
        Generate display-ready leaderboard data.
        This function converts the raw leaderboard data into rendered texts.
        """
        data = []
        for entry in self.leaderboard_data:
            data.append({
                'rank_text': self.font.render(str(entry['rank']), True, BLACK),
                'name_text': self.font.render(entry['name'], True, BLACK),
                'level_type_text': self.font.render(entry['level_type'], True, BLACK),
                'seed_text': self.font.render(str(entry['seed']), True, BLACK),
                'date_text': self.font.render(entry['date'], True, BLACK),
                'score_text': self.font.render(str(entry['score']), True, BLACK)
            })
        return data

    def handle_events(self, events):
        for event in events:
            for button in self.buttons:
                button.handle_event(event)

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(WHITE)

        # Draw all buttons (currently only the Back button)
        for button in self.buttons:
            button.draw(screen)

        # Draw the title and header
        screen.blit(self.title, (self.x_pos, self.y_pos))
        screen.blit(self.header, (self.x_pos, self.y_pos + 50))

        # Draw the leaderboard data rows
        for idx, data in enumerate(self.data):
            y_offset = self.y_pos + 80 + idx * self.line_height
            screen.blit(data['rank_text'], (self.x_pos, y_offset))
            screen.blit(data['name_text'], (self.x_pos + 50, y_offset))
            screen.blit(data['level_type_text'], (self.x_pos + 200, y_offset))
            screen.blit(data['seed_text'], (self.x_pos + 350, y_offset))
            screen.blit(data['date_text'], (self.x_pos + 450, y_offset))
            screen.blit(data['score_text'], (self.x_pos + 550, y_offset))
