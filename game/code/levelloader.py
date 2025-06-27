from settings import *
import requests

class LevelLoader:
    def __init__(self, level_url, from_api=True):
        if from_api:
            # Treat input as URL to the level API
            response = requests.get(level_url)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch level from API: {response.status_code}")
            self.level = response.text
        else:
            with open(f'{level_url}.txt', 'r', encoding='utf-16') as file:
                self.level = file.read()

        marker = '>>>'
        if marker in self.level:
            self.level = self.level.split(marker, 1)[1].strip()

        self.grid = self.parse_level(self.level)

    def get_grid(self):
        return self.grid

    def parse_level(self, level_data):
        rows = level_data.split('\n')
        grid = [list(map(int, row.split())) for row in rows if row.strip()]
        return grid