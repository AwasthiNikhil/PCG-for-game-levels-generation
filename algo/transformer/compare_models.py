"""Compare the original Lode Runner transformer with the retrained models.

    .venv/bin/python algo/transformer/compare_models.py <path to TheVGLC> [levels per model]

1. Does the model use its context? Change everything except the last tile and
   see whether the prediction moves.
2. Held-out loss: next-tile cross-entropy on Lode Runner levels none of the
   models trained on (the retrained model's validation levels).
3. Generated levels: walls vs open space and how walls line up, next to the
   real levels of the same game; then the game-side measures (separate areas,
   platforms, reachable space, route) from benchmark.py's solver.
"""
import contextlib
import io
import json
import math
import os
import statistics
import sys
import time

import numpy as np
import torch
from torch import nn

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'api'))
os.chdir(os.path.join(ROOT, 'api'))
from classes.Grid import Grid  # noqa: E402
from classes.transformer.leveltransformergenerator import LevelTransformerGenerator  # noqa: E402
from classes.transformer.tilegpt import EOS, load  # noqa: E402
from classes.transformer.TileGPTLevelGenerator import SOLID, TileGPTLevelGenerator  # noqa: E402
from placement import plan_route  # noqa: E402
from platformize import platformize  # noqa: E402
import random  # noqa: E402
from playability import is_solid  # noqa: E402

VGLC = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 40
W, H = 34, 26  # grid incl. border: 32 x 24 inside, the Lode Runner width


def real_levels(folder):
    path = os.path.join(VGLC, folder, 'Processed')
    return {f: [r.rstrip('\n') for r in open(os.path.join(path, f)) if r.strip()] for f in sorted(os.listdir(path)) if f.endswith('.txt')}


# ---------- 1. context use ----------
@torch.no_grad()
def context_sensitivity(predict, vocab_size, ctx_len, trials=20):
    rng = np.random.default_rng(0)
    same_last, diff_last = [], []
    for _ in range(trials):
        last = int(rng.integers(vocab_size))
        a = list(rng.integers(0, vocab_size, ctx_len - 1)) + [last]
        b = list(rng.integers(0, vocab_size, ctx_len - 1)) + [last]
        same_last.append(np.abs(predict(a) - predict(b)).max())
        c = a[:-1] + [(last + 1) % vocab_size]
        diff_last.append(np.abs(predict(a) - predict(c)).max())
    return float(np.mean(same_last)), float(np.mean(diff_last))


def v1_model():
    g = LevelTransformerGenerator(Grid(4, 4), width=2, height=2)
    return g.model, g.char2idx


@torch.no_grad()
def v1_predict(model):
    return lambda ids: torch.softmax(model(torch.tensor([ids])), -1)[0].numpy()


@torch.no_grad()
def v2_predict(model):
    return lambda ids: torch.softmax(model(torch.tensor([ids]))[0, -1], -1).numpy()


# ---------- 2. held-out loss on Lode Runner ----------
@torch.no_grad()
def v1_heldout_loss(model, c2i, levels, stride=7):
    total, n = 0.0, 0
    for rows in levels:
        text = [c2i[c] for c in ''.join(rows)]  # the original format: rows joined, no separator
        for i in range(100, len(text), stride):
            logits = model(torch.tensor([text[i - 100:i]]))[0]
            total += nn.functional.cross_entropy(logits[None], torch.tensor([text[i]])).item()
            n += 1
    return total / n


# ---------- 3. level statistics ----------
def to_binary(rows, solid):
    return [['2' if ch in solid else '1' for ch in r] for r in rows]


def wall_stats(g):
    """wall share, mean horizontal wall run, mean vertical wall run"""
    cells = sum(len(r) for r in g)
    walls = sum(r.count('2') for r in g)
    def runs(lines):
        out = []
        for line in lines:
            k = 0
            for ch in list(line) + ['1']:
                if ch == '2':
                    k += 1
                elif k:
                    out.append(k)
                    k = 0
        return out
    h = runs(g)
    v = runs([[g[y][x] for y in range(len(g))] for x in range(len(g[0]))])
    return walls / cells, statistics.mean(h or [0]), statistics.mean(v or [0])


def game_stats(grid):
    open_cells = sum(r.count('1') for r in grid)
    seen, areas = set(), 0
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            if grid[y][x] == '1' and (x, y) not in seen:
                areas += 1
                stack = [(x, y)]
                seen.add((x, y))
                while stack:
                    cx, cy = stack.pop()
                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]) and grid[ny][nx] == '1' and (nx, ny) not in seen:
                            seen.add((nx, ny))
                            stack.append((nx, ny))
    platforms = sum(1 for y in range(len(grid)) for x in range(len(grid[0]))
                    if grid[y][x] == '1' and is_solid(grid, x, y + 1) and not (x > 0 and grid[y][x - 1] == '1' and is_solid(grid, x - 1, y + 1)))
    plan = plan_route(grid)
    return {'open': open_cells / (len(grid) * len(grid[0])), 'areas': areas, 'platforms': platforms,
            'reach': plan['reach_share'] if plan else 0, 'route': plan['route'] if plan else 0}


def generate(kind, seed):
    g = Grid(W, H)
    with contextlib.redirect_stdout(io.StringIO()):
        if kind == 'v1':
            LevelTransformerGenerator(g, width=W - 2, height=H - 2).generate(seed=seed)
            return [row[:] for row in g.grid]
        TileGPTLevelGenerator(g, kind.replace('+post', '')).generate(seed=seed)
    cells = [row[:] for row in g.grid]
    if kind.endswith('+post'):
        platformize(cells, random.Random(seed))
    return cells


def main():
    out = {}
    lr_real, mario_real = real_levels('Lode Runner'), real_levels('Super Mario Bros')
    v1, c2i = v1_model()
    lr2, lr2_cfg = load(os.path.join('classes', 'transformer', 'models', 'loderunner'))
    mario, mario_cfg = load(os.path.join('classes', 'transformer', 'models', 'mario'))

    # 1. context
    out['context'] = {
        'Lode Runner (original)': context_sensitivity(v1_predict(v1), len(c2i), 100),
        'Lode Runner (retrained)': context_sensitivity(v2_predict(lr2), len(lr2_cfg['vocab']), lr2.context),
        'Super Mario Bros': context_sensitivity(v2_predict(mario), len(mario_cfg['vocab']), mario.context),
    }
    # 2. held-out Lode Runner loss (the retrained model's validation levels)
    held = [lr_real[f] for f in lr2_cfg['val_levels']]
    v1_loss = v1_heldout_loss(v1, c2i, held)
    out['heldout'] = {
        'Lode Runner (original)': {'loss': round(v1_loss, 3), 'perplexity': round(math.exp(v1_loss), 2)},
        'Lode Runner (retrained)': {'loss': lr2_cfg['best_val_loss'], 'perplexity': lr2_cfg['best_val_perplexity']},
        'Super Mario Bros': {'loss': mario_cfg['best_val_loss'], 'perplexity': mario_cfg['best_val_perplexity'],
                             'note': 'on held-out Mario levels'},
    }
    # 3. levels
    real = {
        'Lode Runner (real)': [to_binary(r, SOLID['loderunner']) for r in lr_real.values()],
        'Super Mario Bros (real)': [to_binary(r, SOLID['mario']) for r in mario_real.values()],
    }
    out['levels'] = {}
    for name, levels in real.items():
        s = [wall_stats(g) for g in levels]
        out['levels'][name] = {'walls': statistics.mean(a for a, _, _ in s), 'h_run': statistics.mean(b for _, b, _ in s), 'v_run': statistics.mean(c for _, _, c in s)}
    for name, kind in (('Lode Runner (original)', 'v1'), ('Lode Runner (retrained)', 'loderunner'), ('Super Mario Bros', 'mario'),
                       ('Super Mario Bros + post-processing', 'mario+post')):
        rows, times = [], []
        for i in range(N):
            t0 = time.perf_counter()
            grid = generate(kind, f'cmp-{kind}-{i}')
            times.append(time.perf_counter() - t0)
            inner = [r[1:-1] for r in grid[1:-1]]
            rows.append((wall_stats(inner), game_stats(grid)))
        mean = lambda f: statistics.mean(f(r) for r in rows)
        out['levels'][name] = {
            'walls': mean(lambda r: r[0][0]), 'h_run': mean(lambda r: r[0][1]), 'v_run': mean(lambda r: r[0][2]),
            'open': mean(lambda r: r[1]['open']), 'areas': mean(lambda r: r[1]['areas']), 'platforms': mean(lambda r: r[1]['platforms']),
            'reach': mean(lambda r: r[1]['reach']), 'route': statistics.median(r[1]['route'] for r in rows),
            'seconds': statistics.median(times),
        }
        print(f'  {name}: done', file=sys.stderr)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
