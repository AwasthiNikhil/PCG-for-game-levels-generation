"""Train a TileGPT on VGLC levels (Super Mario Bros or Lode Runner).

    .venv/bin/python algo/transformer/train_tilegpt.py mario      <path to TheVGLC>
    .venv/bin/python algo/transformer/train_tilegpt.py loderunner <path to TheVGLC>

Data: The Video Game Level Corpus, https://github.com/TheVGLC/TheVGLC (MIT).
Writes api/classes/transformer/models/<name>.pt and .json (weights, vocabulary,
settings and the loss curve).

What's different from the first model (see docs/transformer-experiments.md):
attention along the level with a causal mask, an end-of-slice token, slices
in the direction the game is read (columns for Mario, rows for Lode Runner),
an embedding for each tile's place in its slice, windows that start on a slice
boundary, a next-token loss at every position, held-out levels and
best-checkpoint saving.
"""
import json
import math
import os
import random
import sys
import time

import torch
from torch import nn

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'api'))
from classes.transformer.tilegpt import EOS, TileGPT  # noqa: E402

GAMES = {
    # folder, slice direction
    'mario': ('Super Mario Bros', 'columns'),
    'loderunner': ('Lode Runner', 'rows'),
}
SEED = 7
CONTEXT = 256
STEPS = 3000
BATCH = 32
LR = 3e-4
EVAL_EVERY = 150
VAL_SHARE = 0.15


def read_levels(vglc, folder):
    path = os.path.join(vglc, folder, 'Processed')
    levels = []
    for name in sorted(os.listdir(path)):
        if name.endswith('.txt'):
            with open(os.path.join(path, name)) as f:
                rows = [r.rstrip('\n') for r in f if r.strip()]
            levels.append((name, rows))
    return levels


def serialise(rows, direction):
    slices = rows if direction == 'rows' else [''.join(r[x] for r in rows) for x in range(len(rows[0]))]
    return ''.join(s + EOS for s in slices), len(slices[0])


def main(game, vglc):
    folder, direction = GAMES[game]
    random.seed(SEED)
    torch.manual_seed(SEED)
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'

    levels = read_levels(vglc, folder)
    random.shuffle(levels)
    n_val = max(1, round(len(levels) * VAL_SHARE))
    val_levels, train_levels = levels[:n_val], levels[n_val:]
    texts = {name: serialise(rows, direction) for name, rows in levels}
    slice_len = texts[levels[0][0]][1]
    vocab = sorted({c for text, _ in texts.values() for c in text})
    idx = {c: i for i, c in enumerate(vocab)}
    encode = lambda name: torch.tensor([idx[c] for c in texts[name][0]], dtype=torch.long)
    train = [encode(n) for n, _ in train_levels]
    val = [encode(n) for n, _ in val_levels]

    period = slice_len + 1
    ctx = CONTEXT - CONTEXT % period                     # whole slices per window

    def batch(data, size):
        xs, ys = [], []
        for _ in range(size):
            t = random.choice(data)
            i = random.randint(0, (len(t) - ctx - 1) // period) * period   # start on a slice boundary
            xs.append(t[i:i + ctx])
            ys.append(t[i + 1:i + ctx + 1])
        return torch.stack(xs).to(device), torch.stack(ys).to(device)

    @torch.no_grad()
    def val_loss():
        """Mean next-tile loss on held-out levels, over tile positions only
        (end-of-slice tokens are forced at generation time, so they're excluded)."""
        model.eval()
        total, count = 0.0, 0
        for t in val:
            for i in range(0, len(t) - ctx - 1, (ctx // 2) // period * period):
                x, y = t[i:i + ctx][None].to(device), t[i + 1:i + ctx + 1].to(device)
                logits = model(x)[0]
                keep = y != idx[EOS]
                total += nn.functional.cross_entropy(logits[keep], y[keep], reduction='sum').item()
                count += int(keep.sum())
        model.train()
        return total / count

    settings = dict(context=CONTEXT, d_model=128, nhead=4, num_layers=4, dim_feedforward=512, dropout=0.1)
    model = TileGPT(len(vocab), slice_len, **settings).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=0.01)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=LR, total_steps=STEPS, pct_start=0.1)

    out_dir = os.path.join(ROOT, 'api', 'classes', 'transformer', 'models')
    os.makedirs(out_dir, exist_ok=True)
    prefix = os.path.join(out_dir, game)
    best, curve, t0 = math.inf, [], time.time()
    for step in range(1, STEPS + 1):
        x, y = batch(train, BATCH)
        loss = nn.functional.cross_entropy(model(x).reshape(-1, len(vocab)), y.reshape(-1))
        opt.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        sched.step()
        if step % EVAL_EVERY == 0 or step == STEPS:
            v = val_loss()
            curve.append({'step': step, 'train_loss': round(loss.item(), 4), 'val_loss': round(v, 4)})
            print(f'step {step:5d}  train {loss.item():.3f}  val {v:.3f}  ({time.time() - t0:.0f}s)', flush=True)
            if v < best:
                best = v
                torch.save(model.state_dict(), prefix + '.pt')

    with open(prefix + '.json', 'w') as f:
        json.dump({
            'game': folder, 'direction': direction, 'slice_len': slice_len, 'vocab': vocab,
            'model': settings, 'parameters': sum(p.numel() for p in model.parameters()),
            'train_levels': [n for n, _ in train_levels], 'val_levels': [n for n, _ in val_levels],
            'best_val_loss': round(best, 4), 'best_val_perplexity': round(math.exp(best), 3),
            'steps': STEPS, 'batch': BATCH, 'lr': LR, 'seconds': round(time.time() - t0),
            'curve': curve,
        }, f, indent=1)
    print(f'best held-out loss {best:.3f} (perplexity {math.exp(best):.2f}) → {prefix}.pt')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
