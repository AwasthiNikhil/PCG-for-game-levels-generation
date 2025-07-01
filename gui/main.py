# main.py

import pygame
from settings import WIDTH, HEIGHT, FPS, TITLE
from core.scene_manager import SceneManager
from game_states.menu import MenuScene

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.paused = False
        self.settings = {
            'WIDTH': 25,
            'HEIGHT': 25,
            'SCALE': 2.0,
            'FULLSCREEN': False,
            'VSYNC': False,
            'MASTER_VOL': 1.0,
            'MUSIC_VOL': 0.7,
            'SFX_VOL': 0.7,
        }
        self.scene_manager = SceneManager(MenuScene(self))

    def run(self):
        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                        
            self.scene_manager.scene.handle_events(events)
            self.scene_manager.scene.update()
            self.scene_manager.scene.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

if __name__ == "__main__":
    Game().run()
