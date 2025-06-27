# core/scene_manager.py

class SceneManager:
    def __init__(self, starting_scene):
        self.scene = starting_scene

    def go_to(self, new_scene):
        self.scene = new_scene
