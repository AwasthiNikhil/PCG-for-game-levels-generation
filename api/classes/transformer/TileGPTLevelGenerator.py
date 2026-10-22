"""Levels from a trained TileGPT (see tilegpt.py and algo/transformer/train_tilegpt.py).

- 'mario' (type 9): Super Mario Bros columns, 14 tiles tall, generated at
  exactly the requested width. Taller levels stack strips: the upper strip's
  ground becomes a floor with pits that drop into the strip below.
- 'loderunner' (type 10, for comparison only): Lode Runner rows, 32 tiles
  wide; wider levels put blocks side by side.

Only solid tiles become walls. Everything else (ladders, ropes, coins,
enemies) becomes open space, since the game places its own.
"""
import hashlib
import math
from os.path import dirname, join

from .tilegpt import load, sample_slices

SOLID = {
    'mario': set('XSQ?<>[]Bb'),
    'loderunner': set('Bb'),
}
# Sampling temperature. Mario at 1.0 scatters stray blocks; 0.8 reads like real
# Super Mario Bros (0.6 is nearly flat ground). Lode Runner looks right at 1.0.
TEMPERATURE = {'mario': 0.8, 'loderunner': 1.0}
SKY_ROWS = 4  # Mario rows dropped from the top of each strip
_models = {}


def _model(name):
    if name not in _models:
        _models[name] = load(join(dirname(__file__), 'models', name))
    return _models[name]


def _seed_int(seed, part):
    return int(hashlib.sha256(f'{seed}:{part}'.encode()).hexdigest()[:12], 16)


class TileGPTLevelGenerator:
    def __init__(self, grid, model_name):
        self.grid = grid
        self.name = model_name

    def generate(self, seed=None):
        model, cfg = _model(self.name)
        solid = SOLID[self.name]
        W, H = self.grid.width - 2, self.grid.height - 2     # inside the wall border
        cells = [[None] * W for _ in range(H)]

        if cfg['direction'] == 'columns':
            n = cfg['slice_len']                               # 14
            ground = '-' * (n - 1) + 'X'
            # Mario's top rows are almost always sky, and this game's player jumps
            # lower than Mario. Dropping them stacks the strips closer together.
            used = n - SKY_ROWS
            strips = math.ceil(H / used)
            for s in range(strips):                            # bottom strip first
                cols = sample_slices(model, cfg, W, _seed_int(seed, s), [ground] * 3, TEMPERATURE[self.name])
                for x, col in enumerate(cols):
                    for r, ch in enumerate(col[SKY_ROWS:]):
                        y = H - 1 - s * used - (used - 1 - r)     # strips stack without overlap
                        if 0 <= y < H:
                            cells[y][x] = ch
        else:
            n = cfg['slice_len']                               # 32
            for b in range(math.ceil(W / n)):
                rows = sample_slices(model, cfg, H, _seed_int(seed, b), ['.' * n], TEMPERATURE[self.name])
                for y, row in enumerate(rows):
                    for x, ch in enumerate(row[:max(0, W - b * n)]):
                        cells[y][b * n + x] = ch

        for y in range(H):
            for x in range(W):
                self.grid.grid[y + 1][x + 1] = '2' if (cells[y][x] or '-') in solid else '1'
