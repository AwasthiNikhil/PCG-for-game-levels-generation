import pygame
import os

class AudioManager:
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.music_path = 'assets/sounds/bg/' 
        self.sfx_path = 'assets/sounds/sfx/' 
        self.sfx = {}
        self._load_sfx()
        self.update_volumes()

    def _load_sfx(self):
        # Example: Load all .wav files from sfx_path
        for filename in os.listdir(self.sfx_path):
            if filename.endswith('.wav'):
                name = os.path.splitext(filename)[0]
                self.sfx[name] = pygame.mixer.Sound(os.path.join(self.sfx_path, filename))

    def play_music(self, filename, loop=-1):
        file_path = os.path.join(self.music_path, filename)
        if os.path.exists(file_path):
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play(loop)
            self.update_volumes()
        else:
            print(f"Warning: Music file not found: {file_path}")

    def stop_music(self):
        pygame.mixer.music.stop()

    def play_sfx(self, name):
        if name in self.sfx:
            self.sfx[name].play()
        else:
            print(f"Warning: SFX not found: {name}")

    def update_volumes(self):
        master_vol = self.settings_manager.get_setting('MASTER_VOL', 1.0)
        music_vol = self.settings_manager.get_setting('MUSIC_VOL', 0.7)
        sfx_vol = self.settings_manager.get_setting('SFX_VOL', 0.7)

        pygame.mixer.music.set_volume(master_vol * music_vol)
        for sound in self.sfx.values():
            sound.set_volume(master_vol * sfx_vol)
