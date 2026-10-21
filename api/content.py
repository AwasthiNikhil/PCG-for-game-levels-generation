"""Place coins, enemies and lava with rules, and measure the level.

Runs after placement.plan_route, so it knows the route from start to key to
exit. Everything goes somewhere the player can reach. Enemy counts per level
match the game's table, and the server's score limit (pcg-db
app/Support/Scoring.php) assumes the same maximums.
"""
from playability import explore, is_solid

# type, first level, +1 every N levels, max, count at first level, min tiles from start
ENEMIES = [
    ('crawler', 2, 3, 3, 1, 5),
    ('cannon', 4, 4, 2, 1, 7),
    ('bat', 5, 3, 3, 1, 6),
    ('hunter', 7, 4, 2, 1, 9),
    ('icicle', 9, 3, 4, 2, 4),
    ('mimic', 12, 4, 2, 1, 6),
    ('phantom', 15, 5, 2, 1, 12),
]


def enemy_count(level, first, every, most, base):
    return 0 if level < first else min(most, base + (level - first) // every)


def time_limit(level, route):
    """Seconds on the clock: grows with the route, never above the level's cap."""
    return max(20, min(30 + 2 * (level - 1), round(12 + route * 0.3)))


def line_of_sight(grid, a, b):
    steps = max(abs(a[0] - b[0]), abs(a[1] - b[1])) * 2
    for i in range(1, steps):
        x = a[0] + (b[0] - a[0]) * i / steps
        y = a[1] + (b[1] - a[1]) * i / steps
        if is_solid(grid, round(x), round(y)):
            return False
    return True


def place_content(grid, plan, level, rng):
    start, key, exit_ = (tuple(plan[k]) for k in ('start', 'key', 'exit'))
    touched, standing, _ = explore(grid, start)
    path = [tuple(c) for c in plan['path']]
    on_route = set(path)
    taken = {start, key, exit_}

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def from_route(c):
        return min(manhattan(c, p) for p in path)

    def free(c, gap):
        return all(manhattan(c, t) > gap for t in taken)

    def air(x, y):
        return not is_solid(grid, x, y)

    def platform(c):
        """Length of the flat walkable run this standing cell is on."""
        x, y = c
        left = right = 0
        while (x - left - 1, y) in standing:
            left += 1
        while (x + right + 1, y) in standing:
            right += 1
        return left + right + 1

    def pick(candidates, n, gap=2, score=None):
        cells = sorted(candidates, key=lambda c: (score(c) if score else 0, rng.random()))
        chosen = []
        for c in cells:
            if len(chosen) == n:
                break
            if free(c, gap):
                chosen.append(c)
                taken.add(c)
        return chosen

    # Coins: half spread along the route, half as far from it as possible
    total = 3 + level
    coins = []
    inner = path[3:-3] or path
    for i in range((total + 1) // 2):
        c = inner[int((i + 0.5) * len(inner) / ((total + 1) // 2))]
        if free(c, 1):
            coins.append(c)
            taken.add(c)
    coins += pick(touched, total - len(coins), gap=2, score=lambda c: -from_route(c))

    # Enemies, by type
    rules = {
        'crawler': lambda c: c in standing and platform(c) >= 3,
        'hunter': lambda c: c in standing and platform(c) >= 4,
        'cannon': lambda c: c in standing and air(c[0], c[1] - 1),
        'bat': lambda c: all(air(c[0] + dx, c[1] + dy) for dx in (0, 1) for dy in (0, 1)) and from_route(c) <= 4,
        'icicle': lambda c: is_solid(grid, c[0], c[1] - 1) and air(c[0], c[1] + 1) and air(c[0], c[1] + 2)
                            and any(p[0] == c[0] and 0 < p[1] - c[1] <= 6 for p in path),
        'mimic': lambda c: c not in on_route and from_route(c) <= 3,
        'phantom': lambda c: True,
    }
    scores = {
        'cannon': lambda c: -sum(1 for p in path if manhattan(c, p) <= 8 and line_of_sight(grid, c, p)),
        'crawler': from_route,
        'bat': from_route,
        'hunter': lambda c: -manhattan(c, start),
        'phantom': lambda c: -manhattan(c, start),
    }
    enemies = []
    for kind, first, every, most, base, min_dist in ENEMIES:
        n = enemy_count(level, first, every, most, base)
        if not n:
            continue
        candidates = [c for c in touched if manhattan(c, start) >= min_dist and rules[kind](c)]
        enemies += [{'type': kind, 'x': c[0], 'y': c[1]} for c in pick(candidates, n, gap=2, score=scores.get(kind))]

    # Lava: one-tile pools, on the route where possible, always hoppable
    lava = []
    if level >= 6:
        want = min(8, 2 + (level - 6) // 2)
        def hoppable(c):
            x, y = c
            return ((x - 1, y) in standing and (x + 1, y) in standing
                    and air(x, y - 1) and air(x - 1, y - 1) and air(x + 1, y - 1) and manhattan(c, start) > 4)
        candidates = [c for c in standing if hoppable(c)]
        for c in sorted(candidates, key=lambda c: (c not in on_route, rng.random())):
            if len(lava) == want:
                break
            if c in taken or any(abs(c[0] - l[0]) <= 1 and c[1] == l[1] for l in lava):
                continue
            lava.append(c)
            taken.add(c)

    # Route shape: how much climbing and dropping it takes
    ups = sum(1 for a, b in zip(path, path[1:]) if b[1] < a[1])
    downs = sum(1 for a, b in zip(path, path[1:]) if b[1] > a[1])
    return {
        'coins': [list(c) for c in coins],
        'enemies': enemies,
        'lava': [list(c) for c in lava],
        'time_limit': time_limit(level, plan['route']),
        'metrics': {'route': plan['route'], 'climb': ups, 'drop': downs, 'reach_share': plan['reach_share']},
    }
