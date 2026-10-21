"""Make cave- and dungeon-style levels work as a side-on platformer.

The older generators were written for top-down maps, so they leave open
spaces too tall to climb and pockets sealed off by thin walls. This pass
repeats three small fixes, rechecking what's reachable each round:

- ledges: a 2-tile platform two tiles up, beside a reachable floor that sits
  under open space too tall to jump into;
- doors: a doorway through a 1–2 tile wall between reachable and unreachable
  floor at walking height;
- ceiling holes: a hole in a 1-tile ceiling with unreachable space above.

The outer border is never touched.
"""
from playability import is_solid, CLIMB
from placement import biggest_region

ROUNDS = 6


def platformize(grid, rng):
    """Edit grid in place; returns the number of changes made."""
    changes = 0
    for _ in range(ROUNDS):
        region = biggest_region(grid)
        if region is None:
            break
        _, touched, standing, _ = region
        made = _ledges(grid, touched, standing, rng) + _doors(grid, touched, standing) + _ceiling_holes(grid, touched, standing)
        changes += made
        if not made:
            break
    return changes


def _inside(grid, x, y):
    return 1 <= x < len(grid[0]) - 1 and 1 <= y < len(grid) - 1


def _air(grid, x, y):
    return _inside(grid, x, y) and grid[y][x] == '1'


def _ledges(grid, touched, standing, rng):
    made, recent = 0, set()
    for (x, y) in sorted(standing, key=lambda c: (c[1], c[0])):
        # tall open space above that the player can't reach yet
        height = 0
        while _air(grid, x, y - height - 1):
            height += 1
        if height <= CLIMB + 1 or (x, y - CLIMB - 1) in touched:
            continue
        if any(abs(x - rx) < 4 and abs(y - ry) < 3 for rx, ry in recent):
            continue  # don't stack ledges on top of each other
        for side in rng.sample((-1, 1), 2):
            cells = [(x + side, y - 2), (x + 2 * side, y - 2)]
            # ledge cells and the headroom above them must be open air, and
            # the floor-level walkway under them stays clear
            if all(_air(grid, cx, cy) and _air(grid, cx, cy - 1) and _air(grid, cx, cy - 2) and _air(grid, cx, cy + 1)
                   for cx, cy in cells):
                for cx, cy in cells:
                    grid[cy][cx] = '2'
                recent.add((x, y))
                made += 1
                break
    return made


def _doors(grid, touched, standing):
    made = 0
    for (x, y) in standing:
        for d in (-1, 1):
            # a wall 1 or 2 thick, with unreachable floor-level air beyond it
            for thick in (1, 2):
                wall = [(x + d * i, y) for i in range(1, thick + 1)]
                beyond = (x + d * (thick + 1), y)
                if (all(_inside(grid, cx, cy) and grid[cy][cx] == '2' for cx, cy in wall)
                        and _air(grid, *beyond) and beyond not in touched):
                    for cx, cy in wall:
                        grid[cy][cx] = '1'
                    made += 1
                    break
    return made


def _ceiling_holes(grid, touched, standing):
    made = 0
    for (x, y) in standing:
        # standing under a 1-thick ceiling with unreachable space right above
        if (_inside(grid, x, y - 1) and grid[y - 1][x] == '2'
                and _air(grid, x, y - 2) and (x, y - 2) not in touched
                and not is_solid(grid, x, y - 3)):
            grid[y - 1][x] = '1'
            made += 1
    return made
