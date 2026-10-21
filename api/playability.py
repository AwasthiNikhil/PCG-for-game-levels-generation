"""Can a level be played with plain movement?

A conservative model of the game's player (pcg/src/gameObjects/Player.js) on
the tile grid: walk, fall off ledges, and jump up to CLIMB tiles high while
moving up to REACH tiles sideways. Each tile fallen gives back one tile of
sideways movement (the real player drifts ~1.5-2 tiles per tile fallen). A
double jump reaches ~4 tiles high; 3 leaves margin. Wall jumps, dashes and
breaking walls are deliberately left out, so a level counts as playable only
if it works without them.

Grid cells: '1' floor (empty air), '2' wall. Coordinates are (x, y), y down.
The world edge counts as solid, as it does in the game.
"""
from collections import deque

CLIMB = 3   # tiles a jump can rise
REACH = 4   # tiles a jump or fall can drift sideways


def is_solid(grid, x, y):
    return not (0 <= y < len(grid) and 0 <= x < len(grid[0])) or grid[y][x] == '2'


def land(grid, x, y):
    """Where something dropped at (x, y) comes to rest, or None if (x, y) is solid."""
    if is_solid(grid, x, y):
        return None
    while not is_solid(grid, x, y + 1):
        y += 1
    return (x, y)


def explore(grid, start, climb=CLIMB, reach=REACH):
    """Breadth-first search over movement states from start (a floor cell).

    Returns (touched, standing, steps):
      touched  every cell the player's body can pass through
      standing cells the player can stand in (floor below)
      steps    fewest moves to reach each touched cell
    """
    origin = land(grid, *start)
    if origin is None:
        return set(), set(), {}
    # state: (x, y, phase, up_used, side_used); phase 'g' ground, 'r' rising, 'f' falling
    first = (origin[0], origin[1], 'g', 0, 0)
    queue = deque([(first, 0)])
    seen = {first}
    steps = {origin: 0}
    standing = {origin}

    def push(state, d):
        if state in seen:
            return
        seen.add(state)
        cell = (state[0], state[1])
        if cell not in steps:
            steps[cell] = d
        queue.append((state, d))

    while queue:
        (x, y, phase, up, side), d = queue.popleft()
        d += 1
        if phase == 'g':
            standing.add((x, y))
            for dx in (-1, 1):
                nx = x + dx
                if is_solid(grid, nx, y):
                    continue
                if is_solid(grid, nx, y + 1):
                    push((nx, y, 'g', 0, 0), d)          # walk
                else:
                    push((nx, y, 'f', 0, 1), d)          # walk off a ledge
            if not is_solid(grid, x, y - 1):
                push((x, y - 1, 'r', 1, 0), d)           # jump
            continue
        # in the air
        if phase == 'r' and up < climb and not is_solid(grid, x, y - 1):
            push((x, y - 1, 'r', up + 1, side), d)
        if side < reach:
            for dx in (-1, 1):
                if not is_solid(grid, x + dx, y):
                    push((x + dx, y, phase, up, side + 1), d)
        if is_solid(grid, x, y + 1):
            push((x, y, 'g', 0, 0), d)                   # land
        else:
            push((x, y + 1, 'f', up, max(0, side - 1)), d)  # fall (also ends a rise); drift regained

    return set(steps), standing, steps


def _demo():
    # a 3-high step is climbable, a 4-high one isn't
    grid = [list(r) for r in [
        "2222222222",
        "2111111112",
        "2111111222",
        "2111112222",
        "2111122222",
        "2111222222",
        "2222222222",
    ]]
    touched, standing, _ = explore(grid, (1, 5))
    assert (4, 4) in standing, "one-tile step up"
    assert (8, 1) in touched, "top ledge reached by climbing the stairs"
    wall = [list(r) for r in [
        "22222",
        "21112",
        "21122",
        "21122",
        "21122",
        "21122",
        "22222",
    ]]
    touched, standing, _ = explore(wall, (1, 5))
    assert (3, 1) not in standing, "a 4-tile wall is too tall"
    # a long fall lets you drift further than a jump alone
    drop = [list(r) for r in [
        "2222222222",
        "2112222222",
        "2111111112",
        "2111111112",
        "2111111112",
        "2111111112",
        "2111111122",
        "2222222222",
    ]]
    touched, standing, _ = explore(drop, (1, 1))
    assert (8, 5) in standing, "drift 7 tiles across while falling 4"
    print("playability self-check passed")


if __name__ == "__main__":
    _demo()
