# main.py

import pygame
from settings import WIDTH, HEIGHT, FPS, TITLE
from core.scene_manager import SceneManager
from game_states.menu import MenuScene
from utils.settings_manager import SettingsManager
from core.audio_manager import AudioManager

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.paused = False
        
        self.player_speed = 200
        self.jump_height = 200

        self.settings_manager = SettingsManager() 
        self.audio_manager = AudioManager(self.settings_manager)
        self.audio_manager.play_music("bgm1.ogg")
        self.settings = {
            'FULLSCREEN': self.settings_manager.get_setting('FULLSCREEN', False),
            'MASTER_VOL': self.settings_manager.get_setting('MASTER_VOL', 1.0),
            'MUSIC_VOL': self.settings_manager.get_setting('MUSIC_VOL', 0.7),
            'SFX_VOL': self.settings_manager.get_setting('SFX_VOL', 0.7)            
        }
        self.settings_manager.save_settings(self.settings)  
        self.player_speed = 200
        self.jump_height = 200
        
        self.scene_manager = SceneManager(MenuScene(self))

    def run(self):
        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                    self.settings_manager.save_settings(self.settings) 
                        
            self.scene_manager.scene.handle_events(events)
            self.scene_manager.scene.update()
            self.scene_manager.scene.draw(self.screen)

            pygame.display.flip()
            self.dt = self.clock.tick()/1000

        pygame.quit()

if __name__ == "__main__":
    Game().run()
