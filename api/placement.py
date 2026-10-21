"""Place the start, key and exit on a route the player can actually take.

Uses the solver in playability.py, so a placed level is playable by
construction: the key is reachable from the start, and the exit from the key.
"""
from playability import explore, is_solid

MAX_REGIONS = 12        # start candidates to try, each in a different region
MIN_REACH_SHARE = 0.35  # a good level lets you reach at least this share of its open cells
MIN_ROUTE = 18          # ...and the start → key → exit route is at least this many moves


def standable_cells(grid):
    return [(x, y) for y in range(len(grid)) for x in range(len(grid[0]))
            if grid[y][x] == '1' and is_solid(grid, x, y + 1)]


def biggest_region(grid):
    """Explore from starts in different regions; return the one with the most
    standing room as (start, touched, standing, steps), or None."""
    cells = standable_cells(grid)
    if not cells:
        return None
    best, covered, tried = None, set(), 0
    for cell in sorted(cells, key=lambda c: c[0] + c[1]):  # top-left first, like before
        if cell in covered:
            continue
        touched, standing, steps = explore(grid, cell)
        covered |= standing
        tried += 1
        if best is None or len(standing) > len(best[2]):
            best = (cell, touched, standing, steps)
        if tried >= MAX_REGIONS:
            break
    return best


def route_cells(steps, target):
    """Cells on a shortest route to target, walking back through the step counts."""
    path, cell = [target], target
    while steps.get(cell, 0) > 0:
        x, y = cell
        cell = min(((x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if (x + dx, y + dy) in steps),
                   key=lambda c: steps[c])
        path.append(cell)
    return path[::-1]


def plan_route(grid):
    """Return {start, key, exit, route, reach_share, path} or None if there's nowhere to stand."""
    region = biggest_region(grid)
    if region is None:
        return None
    open_cells = sum(row.count('1') for row in grid)
    start, touched, standing, steps = region

    # Key: the reachable standing spot farthest from the start.
    key = max(standing, key=lambda c: (steps[c], c))
    # Exit: reachable from the key and as far as possible from whichever of the
    # start and key is nearer. In a linear level that's mid-route: you pass the
    # locked exit on the way to the key, then come back.
    _, from_key_standing, from_key = explore(grid, key)
    exits = [c for c in from_key_standing if c not in (start, key)]
    if not exits:
        return None
    exit_ = max(exits, key=lambda c: (min(from_key[c], steps.get(c, from_key[c])), from_key[c], c))

    return {
        "start": list(start),
        "key": list(key),
        "exit": list(exit_),
        "route": steps[key] + from_key[exit_],
        "reach_share": round(len(touched) / max(1, open_cells), 3),
        # cells along start → key → exit, for placing things on or off the route
        "path": route_cells(steps, key) + route_cells(from_key, exit_)[1:],
    }


def good_enough(plan):
    return plan is not None and plan["reach_share"] >= MIN_REACH_SHARE and plan["route"] >= MIN_ROUTE


def _demo():
    # two rooms joined by a step: start bottom-left, key and exit spread out
    grid = [list(r) for r in [
        "222222222222",
        "211111111112",
        "211111111112",
        "211112211112",
        "211112211112",
        "211112211112",
        "222222222222",
    ]]
    plan = plan_route(grid)
    assert plan and plan["key"] != plan["start"] and plan["exit"] not in (plan["key"], plan["start"])
    _, standing, _ = explore(grid, tuple(plan["start"]))
    assert tuple(plan["key"]) in standing
    gap = lambda a, b: abs(a[0] - b[0]) + abs(a[1] - b[1])
    assert gap(plan["exit"], plan["key"]) >= 3 and gap(plan["exit"], plan["start"]) >= 3, "exit away from both"
    print("placement self-check passed", plan)


if __name__ == "__main__":
    _demo()
