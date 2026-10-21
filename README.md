# PCG for game levels

Procedural level generation for **Lucky You**, a 2D tile game. This repo
holds the generators and the Flask API that serves them. It is one of three
repos:

| Repo | What it is |
|---|---|
| **PCG-for-game-levels-generation** (this one) | Level generators and the Flask API |
| [pcg](https://github.com/AwasthiNikhil/pcg) | The web game (Phaser 3 + Vite) |
| [pcg-db](https://github.com/AwasthiNikhil/pcg-db) | Accounts, scores, shop and the admin dashboard (Laravel 13) |

## Generators

Every generator fills the same grid: `1` is floor and `2` is wall.

| Type | Generator | How it works |
|---|---|---|
| 1 | Random | Each cell becomes a wall with `wall_probability`, then isolated walls are removed |
| 2 | Perlin noise | A native Perlin implementation, cut at `threshold` |
| 3 | Simplex noise | A native 2D Simplex implementation; `scale` sets the feature size |
| 4 | Cellular automata | A random fill, smoothed for `iterations` rounds |
| 5 | BSP | Binary space partitioning into rooms |
| 6 | Graph | Rooms that don't overlap, joined by L-shaped corridors |
| 7 | Transformer | A small character-level transformer (PyTorch) trained on level text. It lives in `api/classes/transformer/` |

As levels get harder, the web game moves through types 1, 4, 6, 2 and 7.
See `src/levels.js` in the `pcg` repo.

## Run the API

You need Python 3.9 or newer.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cd api                      # model paths are relative to api/
../.venv/bin/python main2.py
```

The API listens on `http://127.0.0.1:5055`. Set `PORT` to use a different
port. It doesn't use Flask's default of 5000 because macOS uses 5000 for
AirPlay.

```
GET /generate/<type>?x=25&y=25&seed=42
```

All query parameters are optional:

| Param | Default | Used by |
|---|---|---|
| `x`, `y` | 25, 25 | all types (grid width and height) |
| `seed` | random | all types |
| `wall_probability` | 45 (a percent) | 1, 4 |
| `threshold` | 0 (a percent) | 2, 3 |
| `scale` | 6 | 3 |
| `iterations` | 1 | 4 |
| `min_leaf_size`, `max_leaf_size` | 8, 15 | 5 |
| `max_rooms`, `min_room_size`, `max_room_size` | 15, 3, 8 | 6 |

Example response:

```json
{ "metadata": { "seed": "42", "level_type": 6, "width": 25, "height": 25 },
  "grid": [["2", "2", "1", ...], ...] }
```

To check every generator, run this from the repo root. It includes parameter
combinations that used to crash.

```sh
.venv/bin/python check_generators.py
```

## `main.py` vs `main2.py`

- **`api/main2.py`** is the JSON API the web game uses.
- **`api/main.py`** is the original API for the desktop game. It returns
  levels as plain text. It also adds `/login`, `/settings` and
  `/level/<user>` routes backed by PostgreSQL.

## Desktop game (legacy)

`game/` is the first version of the game, written in pygame. The web game
replaced it, and it's kept for reference. It hasn't been run since the 2026
revamp.

It expects two things:

- `api/main.py` running on port 5000
- a PostgreSQL database named `game`, owned by `game_user`, as configured in
  `api/database/NetworkManager.py`. The schema isn't in this repo.

```sh
cd game && ../.venv/bin/python main.py
```

## Other folders

| Folder | Contents |
|---|---|
| `algo/` | Experiments that aren't wired into the API: drunkard's walk, a genetic algorithm (needs `deap`), an LSTM and an earlier transformer |
| `model/` | Trained LSTM and transformer weights from those experiments |
| `worldgeneration/` | An earlier copy of the generator classes |
| `game_learnings/` | pygame tutorial projects from learning the engine |
| `diagrams/`, `out/` | PlantUML sources and the rendered UML diagrams |
