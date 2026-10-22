# Transformer experiments: Lode Runner vs Super Mario Bros

The game's machine-learning generator was a small transformer trained on the
Lode Runner levels of [The Video Game Level Corpus](https://github.com/TheVGLC/TheVGLC)
(VGLC). This document covers four things:

- how that model was trained;
- what was wrong with it;
- a retrained Lode Runner model;
- a new model trained on VGLC's Super Mario Bros levels.

The results are compared both as models and as levels in this game.

## TL;DR

- **The original model ignored everything except the previous tile.** Its
  transformer layer was created without `batch_first=True`, so attention ran
  across the 64 samples in a batch instead of along the level. Changing the
  99 tiles of history changes its prediction by exactly 0.00. In effect it's
  a first-order Markov chain over tiles.
- **Fixing the training** gives a Lode Runner model that uses its context and
  predicts held-out levels better: loss 0.961 → 0.839, perplexity 2.61 → 2.31.
  Its levels have longer brick runs and fewer walls, closer to real Lode Runner.
- **The Super Mario Bros model is the most faithful of the three.** Its
  horizontal wall runs average 5.4 tiles against 5.2 in real Mario levels, and
  its held-out perplexity is 1.25.
- **Fidelity is not playability.** The more faithfully a model reproduces
  Mario or Lode Runner, the harder its levels are for this game's player. Mario
  relies on higher jumps and Lode Runner on ladders, and this game has neither.
  The broken original model has the most reachable levels (95%) precisely
  because its output is scattered noise that's easy to climb. The Mario model
  needs the platformer post-processing to be playable here (39% → 62% reachable).

## The original training 

| | Original | Assessment |
|---|---|---|
| Data | 150 VGLC Lode Runner levels (32×22) | ✓ Good, a clean public corpus |
| Serialisation | every row of every level joined into one string, **no row separator** | ✗ "The tile below" is invisible to the model |
| Context | the last 100 tiles (about 3 rows) | ✗ Too short for 2D structure |
| Model | `nn.TransformerEncoder`, 4 layers, d=128, 4 heads | ✓ A reasonable size |
| Layer setup | `TransformerEncoderLayer(...)` **without `batch_first=True`**, fed `(batch, seq, dim)` | ✗ **The main bug.** Attention ran across batch samples, not along the level |
| Output | logits of the last position only | ✗ Wastes 99 of every 100 training positions |
| Embedding scale | `× √(sequence length)` | ✗ Should be √d_model (minor) |
| Training | 10 epochs at a learning rate of 5e-5, with **no held-out data** | ✗ No way to see the model failing |
| Sampling | seeded through `numpy`'s global state | ✗ Not reproducible in the API (since fixed) |
| Tile mapping | `B`/`b` → wall, everything else → open | ~ Fair, but ladders and ropes, which Lode Runner levels depend on, become open air |

The bug is easy to confirm on the deployed model. Give it two different
100-tile histories that end in the same tile, and the predicted probabilities
are identical. Change only the last tile, and they move by up to 0.45.

## What changed (`api/classes/transformer/tilegpt.py`, `algo/transformer/train_tilegpt.py`)

- **Attention along the level**, with `batch_first=True` and a causal mask.
- **One slice at a time, with an end-of-slice token:** rows for Lode Runner,
  and columns for Mario, because it's a side-scroller.
- **An embedding for each tile's place in its slice.** This was added after the
  first Mario run, which had a good loss (perplexity 1.44) but predicted sky
  where the ground belongs. It couldn't tell which row of a column it was on.
  With the embedding (and windows that start on a slice boundary), held-out
  perplexity dropped to 1.25 and the ground lines appeared.
- **A longer context:** 255 tiles (17 Mario columns) or 231 tiles (7 Lode
  Runner rows).
- **A loss at every position.**
- **Held-out levels** (15%), the best checkpoint kept, AdamW with a one-cycle
  schedule, 3,000 steps of 32 windows.
- **Generation that forces the end-of-slice token,** so every slice has the
  right length, and a seeded `torch.Generator`.
- **Temperature 0.8 for Mario** (1.0 scattered stray blocks; 0.6 was nearly
  flat ground), and 1.0 for Lode Runner.

The same model size (d=128, 4 layers, 4 heads, about 0.8M parameters) and the
same data are used, so the comparison is about the training, not the
capacity. Each model trains in about 5 minutes on an Apple M5.

## Results

`algo/transformer/compare_models.py`, 40 generated levels per model, each on a
34×26 grid (32×24 inside the border).

### As models

| | Original Lode Runner | Retrained Lode Runner | Super Mario Bros |
|---|---|---|---|
| Prediction change when the 99-tile history changes | **0.000** | 0.078 | 0.035 |
| Prediction change when only the last tile changes | 0.446 | 0.561 | 0.850 |
| Held-out loss (perplexity) | 0.961 (2.61) | **0.839 (2.31)** | 0.224 (1.25)\* |

\* On held-out Mario levels. Mario is mostly sky, so its loss isn't
comparable with Lode Runner's.

### How the levels look, next to the real thing

Walls are the share of wall tiles. Runs are the average length of a
horizontal or vertical stretch of wall.

| | Walls | Horizontal run | Vertical run |
|---|---|---|---|
| Real Lode Runner | 27% | 5.0 | 2.0 |
| Original Lode Runner model | 33% | 2.9 | 1.5 |
| Retrained Lode Runner model | 24% | 3.3 | 1.5 |
| Real Super Mario Bros | 13% | 5.2 | 1.5 |
| Mario model | 15% | **5.4** | 1.3 |

The Mario model reproduces Mario's long ground lines almost exactly. Retraining
moves Lode Runner closer to the real thing on wall share and horizontal runs,
but vertical structure (columns of bricks) is still under-learned by both
Lode Runner models.

### As levels in this game

| | Separate areas | Platforms | Reachable space | Median route | Generation time |
|---|---|---|---|---|---|
| Original Lode Runner model | 7.0 | 79 | **92%** | 120 | 0.6 s |
| Retrained Lode Runner model | 5.0 | 50 | 86% | 98 | 1.3 s |
| Mario model | 3.8 | 20 | 39% | 61 | 2.4 s |
| Mario model + post-processing | 2.6 | 28 | 62% | 82 | 2.4 s |

Through the full API (route planning, regeneration, level-sized grids;
`benchmark.py`), every model is 100% playable. Reachable space is 95%
(original Lode Runner), 86% (retrained Lode Runner) and 78% (Mario with
post-processing).

## Samples (raw tiles)

Original Lode Runner model. Ladders (`#`) never line up, and brick runs are
short and broken:

```
....#..##bb..bbbbbb#B.E#bb.Gb#b#
................#b#bbbbbb.......
-----------.bbb......bG.#..bbGb.
...#bb.....#b..##--.G...........
.###..#..G.....bbbbb.BBBB..##BBb
#BBBBBBBB....bbbBB.##.....#-----
```

Retrained Lode Runner model. Long brick floors, ropes, and the spawn point near the top. Ladders appear, but they don't line up reliably yet:

```
...M.....E.......bbb#BBBBBbBBBbb
bbbbBbbB...........bbbbBbbBBBBbB
b--#bbbbb..bBbBBb#bbBBbbbbbbbbb-
bbbbb....bbbbbbbbbbbb..........B
B.........GGb.....bb-.......#..B
```

Mario model, temperature 0.8. Ground with pits, a pipe, a Bullet Bill cannon,
enemies on the ground, and blocks at jump height:

```
-------------------------------------------------------?SSS--S--------
-----------------------------------------------------<E-----S---------
---E-------------------------------------------------[>---------------
-------------------------------B---------------------[]---------------
--E--E-------------------------b--E------------------[]---------------
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX-XXX--XXXXXXXXXXXXXXXXXXX
```

## What we did right and wrong

**Right**
- Using a real, well-known corpus (VGLC), not hand-made levels.
- A transformer is a sensible model for tile sequences; the size was fine.
- Mapping the source's tiles down to this game's two tiles kept the integration simple.

**Wrong**
- `batch_first` left at its default, which silently turned the transformer
  into a first-order Markov chain. Nothing caught it, because there was no
  held-out evaluation and no test that the model uses its context.
- Joining rows with no separator and a 3-row context threw away the 2D
  structure the levels are made of.
- Training only on the last position of each window wasted almost all of the data.
- Lode Runner was a poor fit for this game in the first place: its levels
  depend on ladders, ropes and digging, and the game has none of those.

**Lessons**
- **Evaluate before deploying:** a held-out loss and a one-line check that the
  model uses its context would have caught the bug immediately.
- **Give the model the structure you know:** the end-of-slice token and the
  place-in-slice embedding are what made the Mario ground lines appear.
- **Choose training data for the target game, not just availability.** But
  fidelity alone doesn't make levels playable here. The game's own movement
  limits decide that, which is why route planning and post-processing matter
  as much as the model.

## Where the models are used

- **Levels 13–16:** the Mario model (generator type 9), with the platformer post-processing.
- **Levels 17+:** the original Lode Runner model (type 7), unchanged, so the
  game keeps the version its benchmarks were run against.
- The retrained Lode Runner model (type 10) is available in the API for
  comparison, but no level uses it.

## Reproduce

```sh
git clone --depth 1 https://github.com/TheVGLC/TheVGLC.git /tmp/TheVGLC
.venv/bin/python algo/transformer/train_tilegpt.py mario /tmp/TheVGLC
.venv/bin/python algo/transformer/train_tilegpt.py loderunner /tmp/TheVGLC
.venv/bin/python algo/transformer/compare_models.py /tmp/TheVGLC 40
```

The trained weights are in `api/classes/transformer/models/`. Each model's
`.json` holds its settings, the held-out levels and the loss curve.

## Data and credit

Level data from The Video Game Level Corpus, MIT License, Copyright (c) 2016
Adam Summerville, Santiago Ontañón, Sam Snodgrass. Summerville, A. J.,
Snodgrass, S., Mateas, M., and Ontañón, S. (2016). *The VGLC: The Video Game
Level Corpus.* Proceedings of the 7th Workshop on Procedural Content Generation.
