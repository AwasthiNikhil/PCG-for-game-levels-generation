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
| 8 | Rooms | Spelunky-style: a grid of rooms with a guaranteed route, each room stamped from hand-made platformer templates (`api/classes/rooms/`) |

As levels get harder, the web game moves through types 1, 4, 6, 2, 8 and 7.
See `src/levels.js` in the `pcg` repo.

## Run the API

To run the whole game (all three repos), follow
[Run the whole game locally](https://github.com/AwasthiNikhil/pcg#run-the-whole-game-locally)
in the pcg README.

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
{ "metadata": { "seed": "42", "level_type": 6, "width": 25, "height": 25,
                "attempts": 1, "route": 48, "reach_share": 0.81 },
  "grid": [["2", "2", "1", ...], ...],
  "start": [3, 4], "key": [21, 14], "exit": [12, 9] }
```

`start`, `key` and `exit` are `[x, y]` cells, always on a route the player
can take. The API generates the level, then places these three using the
playability solver.

- If the level is poor (under 35% of it reachable, or a route under 18 moves),
  the API regenerates it and keeps the best of up to 5 attempts.
- `seed` is the seed that produced the returned level. Send it back to get
  the same level again.

## Playability

`api/playability.py` is a conservative model of the game's player: walking,
falling with sideways drift, and jumps up to 3 tiles high. Wall jumps and
dashes are left out on purpose, so a level counts as playable only if plain
movement is enough. `api/placement.py` uses it to place the start, key and
exit.

`benchmark.py` measures every generator: how often levels are playable, how
much of the coins can be reached, route length and generation time. `--old`
shows the game's previous placement for comparison.

```sh
.venv/bin/python benchmark.py 200          # from the repo root
.venv/bin/python api/playability.py        # self-checks
```

`REVAMP.md` tracks the generation revamp: the plan, its status, and the
benchmark results before and after.

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
