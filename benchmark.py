"""Playability benchmark for every generator.

    .venv/bin/python benchmark.py [levels per generator] [--old]   (from the repo root)

Requests levels with the same parameters the game sends (pcg/src/levels.js) and
checks with api/playability.py whether the key and exit can be reached with
plain movement. By default the start, key and exit come from the API's route
planner; --old places them the way the game used to (by distance from the
top-left corner, key at random). --raw turns off the platformer post-processing.
Coins are placed the way Game.js does.
Prints a Markdown table.
"""
import contextlib
import io
import os
import random
import statistics
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "api"))
os.chdir(os.path.join(ROOT, "api"))  # model paths are relative to api/

from main2 import app  # noqa: E402
from playability import explore  # noqa: E402

# type: (name, level the benchmark imitates, levels that use it in the game)
GENERATORS = {
    1: ("Random", 2, "1–2"),
    4: ("Cellular automata", 4, "3–4"),
    6: ("Graph", 6, "5–6"),
    2: ("Perlin", 8, "7–8"),
    8: ("Rooms", 10, "9–12"),
    7: ("Transformer", 14, "13+"),
    3: ("Simplex", 6, "not used"),
    5: ("BSP", 6, "not used"),
}


def game_params(level):
    """Mirror of fetchLevelData in pcg/src/levels.js."""
    return {
        "x": 20 + 2 * (level // 2),
        "y": 15 + level // 2,
        "wall_probability": round((0.4 + level * 0.005) * 100, 2),
        "iterations": 1 + level // 5,
        "min_leaf_size": max(5, 8 - level // 10),
        "max_leaf_size": min(20, 15 + level // 10),
        "max_rooms": 7,
    }


def spots_2x2(grid):
    """Mirror of findValid2x2Spots: top-left cells of 2x2 open areas."""
    return [(x, y) for y in range(len(grid) - 1) for x in range(len(grid[0]) - 1)
            if grid[y][x] == grid[y][x + 1] == grid[y + 1][x] == grid[y + 1][x + 1] == '1']


def evaluate(level_json, level, rng, old):
    """Place things (the API's way, or the game's old way); report what can be reached."""
    grid = level_json["grid"]
    spots = spots_2x2(grid)
    if len(spots) < 2:
        return None
    shuffled = spots[:]
    rng.shuffle(shuffled)
    total_coins = max(0, min(3 + level, len(shuffled) - 1))
    coins = shuffled[:total_coins]
    if old or not level_json.get("start"):
        by_corner = sorted(spots, key=lambda s: s[0] ** 2 + s[1] ** 2)
        start, exit_, key = by_corner[0], by_corner[-1], shuffled[total_coins]
    else:
        start, key, exit_ = (tuple(level_json[k]) for k in ("start", "key", "exit"))

    touched, _, steps = explore(grid, start)
    from_key, _, key_steps = explore(grid, key)
    key_ok, exit_ok = key in touched, exit_ in from_key
    return {
        "playable": key_ok and exit_ok,
        "exit": exit_ in touched,
        "coins": sum(c in touched for c in coins) / len(coins) if coins else 1.0,
        "route": steps[key] + key_steps[exit_] if key_ok and exit_ok else None,
        "attempts": level_json["metadata"].get("attempts", 1),
        "reach": len(touched) / max(1, sum(row.count('1') for row in grid)),
    }


def run(n, old=False, raw=False):
    client = app.test_client()
    rng = random.Random(7)
    rows = []
    for gtype, (name, level, used) in GENERATORS.items():
        count = max(10, n // 5) if gtype == 7 else n  # the transformer is slow
        params = game_params(level)
        query = "&".join(f"{k}={v}" for k, v in params.items()) + ("&platformize=0" if raw else "")
        results, times = [], []
        for _ in range(count):
            t0 = time.perf_counter()
            with contextlib.redirect_stdout(io.StringIO()):  # generators print their seed
                res = client.get(f"/generate/{gtype}?{query}")
            times.append((time.perf_counter() - t0) * 1000)
            if res.status_code != 200:
                continue
            r = evaluate(res.get_json(), level, rng, old)
            if r:
                results.append(r)
        ok = [r for r in results if r["playable"]]
        routes = [r["route"] for r in results if r["route"] is not None]
        rows.append([
            name, used, f"{params['x']}×{params['y']}", str(len(results)),
            f"{100 * len(ok) / max(1, len(results)):.0f}%",
            f"{100 * sum(r['exit'] for r in results) / max(1, len(results)):.0f}%",
            f"{100 * statistics.mean(r['coins'] for r in results):.0f}%" if results else "—",
            str(int(statistics.median(routes))) if routes else "—",
            f"{statistics.median(times):.0f} ms",
            f"{100 * statistics.mean(r['reach'] for r in results):.0f}%" if results else "—",
            f"{statistics.mean(r['attempts'] for r in results):.1f}" if results else "—",
        ])
        print(f"  {name}: done", file=sys.stderr)

    head = ["Generator", "Game levels", "Grid", "Levels", "Playable", "Exit reachable", "Coins reachable", "Median route (moves)", "Median generation time", "Reachable space", "Attempts"]
    print("| " + " | ".join(head) + " |")
    print("|" + "---|" * len(head))
    for r in rows:
        print("| " + " | ".join(r) + " |")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    run(int(args[0]) if args else 200, old="--old" in sys.argv, raw="--raw" in sys.argv)
