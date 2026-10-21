# Level generation revamp

Goal: every generated level is playable in the side-on platformer the game is
now. Levels should be designed rather than scattered, and the difference
should be measurable.

Status: `[x]` done and verified · `[~]` in progress · `[ ]` not started

## 1. Measure, then add a playability check

- [x] A movement model matching the game (`api/playability.py`): walk, fall with drift, jumps up to 3 tiles high. Wall jumps and dashes are deliberately left out
- [x] A solver: every tile reachable from a start position, with self-checks
- [x] A benchmark (`benchmark.py`): N levels per generator → playable %, route length, generation time
- [x] Record the baseline numbers for all 7 generators (below)
- [x] Place start, key and exit on a real route (`api/placement.py`): start in the biggest reachable region, key at the farthest reachable spot, exit far from both
- [x] Regenerate poor levels (under 35% reachable, or a route under 18 moves) and keep the best of up to 5 attempts (2 for the transformer)
- [x] The API returns `start`/`key`/`exit` plus the seed used, route length and reachable share; the game uses them (with a fallback for older responses)

## 2. Spelunky-style room generator

- [x] Room grid with a guaranteed route from start to exit (`api/classes/rooms/RoomLevelGenerator.py`, type 8). Rooms off the path connect along their row, so every room is reachable
- [x] Hand-made platformer room templates with variation: 9 templates, '?' cells, random mirroring, and doors/holes carved per room. More templates would add variety
- [x] Wired into the API (type 8) and the game: levels 9–12 are room levels, and the transformer moves to 13+. Menu, How to play and READMEs updated
- [x] Benchmarked: 100% playable and 100% of coins reachable, the only generator to reach every coin. Without the route planner its layouts are 69% playable, so the planner still matters

## 3. Make the existing generators platformer-friendly

- [x] Post-processing step (`api/platformize.py`): ledges under tall open spaces, doorways through 1–2 tile walls, holes in 1-tile ceilings over unreachable space. It repeats until nothing changes, typically 3–13 edits per level. It's seeded, so levels stay reproducible, and `platformize=0` turns it off
- [x] Applied to Random, Cellular automata, Perlin, Simplex, BSP and Graph. Rooms are built for platforming already; the transformer isn't touched
- [x] Benchmarked (`benchmark.py 150` vs `--raw`). Reachable space: Random 73→95%, Cellular automata 93→97%, Graph 89→95%, Simplex 60→70%, BSP 76→88%, Perlin 100%. Coins reachable rise to match. Playable was already 100% from step 1

## 4. Server-side content placement and difficulty metrics

- [~] The generator places coins (along the route and side branches), enemies (by type, with placement rules) and lava: `api/content.py` is written but not yet wired into the API or tested
- [~] Per-level metrics: route length, climb and drop counts, and a time limit from the route length, in `api/content.py`. Not wired in yet
- [ ] The game uses the server's placement instead of random spots
- [ ] Difficulty comes from the metrics, not just the level number

## 5. Reliable seeds

- [x] Same seed + parameters → same level for all 8 generators. Each generator now has its own `random.Random(seed)` (the transformer a seeded NumPy generator), so concurrent requests don't interfere. Verified with 6 concurrent same-seed requests per generator
- [x] The seed is returned with each level, and retries replay the same layout (the game restarts with the same level data)
- [ ] Optional: a daily seed with its own leaderboard

## 6. Transformer

- [ ] Generate-and-test: sample several, keep only levels that pass the solver
- [ ] Optional: retrain on platformer levels (for example Super Mario levels from the Video Game Level Corpus)

## Baseline (before the revamp)

`benchmark.py 200`. Each generator is called with the parameters the game
sends for its level band. The start, key, coins and exit are placed the way
`Game.js` places them. **Playable** means the key and the exit can both be
reached from the start with plain movement: walking, falling, and jumps up to
3 tiles high. The Transformer row uses 40 levels because it's slow.

| Generator | Game levels | Grid | Playable | Exit reachable | Coins reachable | Median route (moves) | Median generation time |
|---|---|---|---|---|---|---|---|
| Random | 1–2 | 22×16 | 38% | 41% | 60% | 29 | 0 ms |
| Cellular automata | 3–4 | 24×17 | 81% | 90% | 84% | 29 | 1 ms |
| Graph | 5–6 | 26×18 | 74% | 98% | 74% | 28 | 0 ms |
| Perlin | 7–8 | 28×19 | 99% | 100% | 100% | 37 | 1 ms |
| Transformer | 9+ | 30×20 | 82% | 90% | 95% | 44 | 497 ms |
| Simplex | not used | 26×18 | 0% | 0% | 20% | 40 | 1 ms |
| BSP | not used | 26×18 | 44% | 62% | 51% | 33 | 0 ms |

What the failures look like:

- **Random:** the start is often sealed in a pocket.
- **Graph:** the key sometimes lands in a room you can only reach by falling in from above.
- **Simplex:** blobs with openings 4+ tiles up.

The game softens this today because dashes break walls, but no level should
need them.

## After step 1

Same benchmark, using the API's route planner (`benchmark.py 200`):

| Generator | Playable | Coins reachable | Median route (moves) | Median generation time | Attempts |
|---|---|---|---|---|---|
| Random | 100% (was 38%) | 83% (was 60%) | 58 (was 29) | 5 ms | 1.0 |
| Cellular automata | 100% (was 81%) | 95% (was 84%) | 60 (was 29) | 8 ms | 1.0 |
| Graph | 100% (was 74%) | 87% (was 74%) | 48 (was 28) | 4 ms | 1.0 |
| Perlin | 100% (was 99%) | 100% | 78 (was 37) | 14 ms | 1.0 |
| Transformer | 100% (was 82%) | 92% (was 95%) | 102 (was 44) | 527 ms | 1.0 |
| Simplex | 100% (was 0%) | 63% (was 20%) | 57 (was 40) | 6 ms | 1.1 |
| BSP | 100% (was 44%) | 76% (was 51%) | 45 (was 33) | 3 ms | 1.0 |

Playable is 100% by construction now, because the start, key and exit come from
the solver's reachable set. Routes roughly doubled, since the key and exit are
placed far apart. Coins are still scattered at random; step 4 places them.

## After step 2

`benchmark.py 200`, with the room generator in the game's lineup:

| Generator | Game levels | Grid | Playable | Coins reachable | Median route (moves) | Median generation time | Attempts |
|---|---|---|---|---|---|---|---|
| Random | 1–2 | 22×16 | 100% | 82% | 58 | 5 ms | 1.0 |
| Cellular automata | 3–4 | 24×17 | 100% | 96% | 62 | 8 ms | 1.0 |
| Graph | 5–6 | 26×18 | 100% | 86% | 48 | 4 ms | 1.0 |
| Perlin | 7–8 | 28×19 | 100% | 100% | 77 | 14 ms | 1.0 |
| Rooms | 9–12 | 30×20 | 100% | 100% | 78 | 5 ms | 1.0 |
| Transformer | 13+ | 34×22 | 100% | 94% | 118 | 640 ms | 1.0 |
| Simplex | not used | 26×18 | 100% | 64% | 61 | 6 ms | 1.1 |
| BSP | not used | 26×18 | 100% | 75% | 44 | 3 ms | 1.0 |

## Log

- 2026-10-21: plan written.
- 2026-10-21: solver and benchmark added; baseline recorded.
- 2026-10-21: step 1 done. Route planning in the API and the game; every generator at 100% playable.
- 2026-10-21: step 2 done. Room generator (type 8) for levels 9–12. Transformer sampling seeded, so all 8 generators reproduce a level from its seed.
- 2026-10-21: step 5 done apart from the optional daily seed: per-call random generators everywhere.
- 2026-10-21: step 3 done: platformer post-processing for the six older generators.
- 2026-10-21: step 4 started: `api/content.py` written. Paused here. Next: wire it into `main2.py` (needs a `level` query parameter), use it in `Game.js`, then benchmark and test.
- 2026-10-21: game bug found while testing room levels: enemies fell through floors, bats flew through walls, and icicles never shattered. Moving enemies were marked immovable, and Arcade physics never separates two immovable bodies. Fixed in the game (`pcg`).
