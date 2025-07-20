import pygame
import threading
import math
import random
from core.base_scene import BaseScene
from utils.levelgenerationrules import Rules
from settings import WHITE, WIDTH, HEIGHT
from utils.levelloader import LevelLoader

class UserLoadGame(BaseScene):
    def __init__(self, game, level_url=None):
        super().__init__(game)
        self.game = game
        
        self.method_type = Rules().get_generator_for_level(self.game.settings['USERID'])
        if not level_url:
            self.game.level_url = self.build_initial_url()
        else:
            self.game.level_url = level_url
        self.loading = True
        
        self.font = pygame.font.SysFont("Arial", 24)
        self.spinner_angle = 0
        self.dot_timer = 0
        self.dot_count = 0
        self.joke_timer = 0

        self.jokes = [
            "Reticulating splines...",
            "Stealing RAM from neighbors...",
            "Dividing by zero (just once)...",
            "Feeding pigeons your save data...",
            "Spinning faster to impress you...",
            "Loading the meaning of life...",
            "Please wait... resisting urge to crash.",
            "Charging flux capacitor...",
            "Assembling spaghetti code...",
            "Calculating the weight of fun...",
            "Consulting the elder gods...",
            "Unzipping infinite monkeys on typewriters...",
            "Feeding bits to the byte beast...",
            "Making things up as we go...",
            "Debugging the debugger...",
            "Polishing pixels...",
            "Aligning the stars...",
            "Reversing entropy...",
            "Summoning rubber duck...",
            "Please do not tap the glass...",
            "Extremely serious business in progress...",
            "Swapping batteries in the simulation...",
            "Quantum tunneling into the mainframe...",
            "Warming up our ones and zeroes...",
            "Talking to servers nicely...",
            "Sacrificing a byte to the god of bugs..."
        ]

        self.joke = random.choice(self.jokes)
        
        self.request_level()
        
    def request_level(self):
        thread = threading.Thread(target=self.load_level_data)
        thread.start()

    def build_initial_url(self):
        url = (
            f'http://127.0.0.1:5000/generate/{self.method_type}'
            f'?x=15'
            f'&y=15'
            f'&seed=123'
            f'&scale=0'
            f'&min_leaf_size=2'
            f'&max_leaf_size=5'
            f'&wall_probability=50'
            f'&threshold=1'
            f'&min_room_size=2'
            f'&max_rooms=5'
            f'&iterations=3'
        )
        return url

    def load_level_data(self):
        url = self.game.level_url
        try:
            level_data = LevelLoader(url).get_grid()
            self.level_data = level_data
            self.loading = False
            from game_states.usergameplay import UserGameplayScene
            self.game.scene_manager.go_to(UserGameplayScene(self.game, self.level_data))              
        except Exception as e:
            self.joke = "Something went wrong!"
            pygame.time.wait(3000)
            self.go_back()

    def go_back(self):
        print("hi")
        from game_states.menu import MenuScene
        self.game.scene_manager.go_to(MenuScene(self.game))

    def handle_events(self, events):
        for event in events:
            if self.loading  and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE :
                self.go_back()

    def update(self):
        if self.loading:
            # Spin spinner
            self.spinner_angle = (self.spinner_angle + 5) % 360

            # Animate dots
            self.dot_timer += self.game.clock.get_time()
            if self.dot_timer > 400:
                self.dot_timer = 0
                self.dot_count = (self.dot_count + 1) % 4

            # Random joke every 5 seconds
            self.joke_timer += self.game.clock.get_time()
            if self.joke_timer > 3000:
                self.joke_timer = 0
                new_joke = random.choice(self.jokes)
                while new_joke == self.joke:
                    new_joke = random.choice(self.jokes)
                self.joke = new_joke
            if pygame.time.get_ticks() > 30000:
                self.loading = False
                self.go_back()

    def draw_spinner(self, screen, center, radius):
        angle_rad = math.radians(self.spinner_angle)
        end_x = center[0] + radius * math.cos(angle_rad)
        end_y = center[1] + radius * math.sin(angle_rad)
        pygame.draw.circle(screen, (200, 200, 200), center, radius, 4)
        pygame.draw.line(screen, (50, 120, 230), center, (end_x, end_y), 6)

    def draw(self, screen):
        screen.fill(WHITE)

        if self.loading:  
            # Spinner
            center = (WIDTH // 2, HEIGHT // 2 - 40)
            self.draw_spinner(screen, center, 40)

            # Loading dots
            dots = "." * self.dot_count
            loading_text = self.font.render(f"Loading{dots}", True, (0, 0, 0))
            loading_rect = loading_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
            screen.blit(loading_text, loading_rect)

            # Joke message
            joke_text = self.font.render(self.joke, True, (100, 100, 100))
            joke_rect = joke_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70))
            screen.blit(joke_text, joke_rect)
        