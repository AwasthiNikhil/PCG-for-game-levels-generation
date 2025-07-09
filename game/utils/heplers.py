import os
import pygame

# Define the root path to the assets directory
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')

def import_image(*subpath, format='png', alpha=True):
    """
    Load a single image from the assets folder.

    :param subpath: Path components under the assets directory (e.g., 'images', 'player')
    :param format: File format, default is 'png'
    :param alpha: Whether to use convert_alpha() or convert()
    :return: Loaded pygame surface
    """
    full_path = os.path.join(ASSETS_DIR, *subpath) + f'.{format}'
    if alpha:
        return pygame.image.load(full_path).convert_alpha()
    return pygame.image.load(full_path).convert()

def import_folder(*subpath):
    """
    Load all images in a folder (sorted numerically) from the assets folder.

    :param subpath: Path components under the assets directory
    :return: List of loaded surfaces
    """
    target_path = os.path.join(ASSETS_DIR, *subpath)
    frames = []

    for folder_path, _, file_names in os.walk(target_path):
        for file_name in sorted(file_names, key=lambda name: int(os.path.splitext(name)[0])):
            full_path = os.path.join(folder_path, file_name)
            frames.append(pygame.image.load(full_path).convert_alpha())
        break  # Only the top directory (avoid recursion)
        
    return frames

def import_audio(*subpath):
    """
    Load all sound files from a folder in the assets directory.

    :param subpath: Path components under the assets directory
    :return: Dictionary of sounds with filenames as keys
    """
    target_path = os.path.join(ASSETS_DIR, *subpath)
    audio_dict = {}

    for folder_path, _, file_names in os.walk(target_path):
        for file_name in file_names:
            name, _ = os.path.splitext(file_name)
            full_path = os.path.join(folder_path, file_name)
            audio_dict[name] = pygame.mixer.Sound(full_path)
        break  # Only the top directory
        
    return audio_dict
