"""Spelunky-style levels: a grid of rooms with a guaranteed route through it.

1. Pick a room in the top row and walk a path: sideways, sometimes down a
   row, until it reaches the bottom row.
2. Each room on the path gets the openings the path needs: left/right doors,
   a hole in the floor where the path drops, a hole in the ceiling where it
   lands. Rooms off the path get doors along their row back to the path, so
   every room can be explored.
3. Every room is stamped from a hand-made template, randomly mirrored, with
   '?' cells that are wall half the time.

The path only ever goes sideways or down, so walking and falling are enough
to get from the first room to the last.
"""
import random

ROOM_W, ROOM_H = 8, 6

# '#' wall, '.' air, '?' wall half the time. Row 5 is the floor; the path walks
# along row 4. Doors, floor holes and ceiling holes are carved on top.
TEMPLATES = [
    ["########",
     "#......#",
     "#......#",
     "#......#",
     "#......#",
     "########"],
    ["########",
     "#......#",
     "#......#",
     "#..##..#",
     "#..##..#",
     "########"],
    ["########",
     "#......#",
     "#.##...#",
     "#....###",
     "#......#",
     "########"],
    ["########",
     "#......#",
     "#......#",
     "#......#",
     "#......#",
     "###..###"],
    ["########",
     "#?....?#",
     "#......#",
     "#.?..?.#",
     "#......#",
     "########"],
    ["########",
     "#......#",
     "#......#",
     "#......#",
     "#..??..#",
     "########"],
    ["########",
     "#......#",
     "#.####.#",
     "#......#",
     "#......#",
     "########"],
    ["########",
     "#...?..#",
     "#..###.#",
     "#......#",
     "#.?....#",
     "########"],
    ["########",
     "#......#",
     "##...?.#",
     "#......#",
     "#...##.#",
     "########"],
]


class RoomLevelGenerator:
    def __init__(self, grid):
        self.grid = grid

    def generate(self, seed=None):
        rng = random.Random(seed)
        W, H = self.grid.width, self.grid.height
        cols = max(1, (W - 2) // ROOM_W)
        rows = max(1, (H - 2) // ROOM_H)
        ox, oy = (W - cols * ROOM_W) // 2, (H - rows * ROOM_H) // 2   # leftover margin stays wall

        openings = {(c, r): set() for c in range(cols) for r in range(rows)}
        path = self._walk_path(rng, cols, rows, openings)

        # Off-path rooms: open doors along the row toward the nearest path room.
        # The path visits every row, so every room ends up reachable.
        for (c, r) in openings:
            if (c, r) in path:
                continue
            target = min((pc for (pc, pr) in path if pr == r), key=lambda pc: abs(pc - c))
            step = 1 if target > c else -1
            for x in range(c, target, step):
                openings[(x, r)].add('R' if step > 0 else 'L')
                openings[(x + step, r)].add('L' if step > 0 else 'R')

        for (c, r), doors in openings.items():
            self._stamp(rng, ox + c * ROOM_W, oy + r * ROOM_H, doors)

    def _walk_path(self, rng, cols, rows, openings):
        c, r = rng.randrange(cols), 0
        path = [(c, r)]
        direction = rng.choice((-1, 1))
        while True:
            go_down = rng.random() < 0.25 or not (0 <= c + direction < cols)
            if not go_down:
                openings[(c, r)].add('R' if direction > 0 else 'L')
                openings[(c + direction, r)].add('L' if direction > 0 else 'R')
                c += direction
            elif r == rows - 1:
                return set(path)                      # the path leaves through the last room
            else:
                openings[(c, r)].add('B')
                openings[(c, r + 1)].add('T')
                r += 1
                direction = rng.choice((-1, 1))
            path.append((c, r))

    def _stamp(self, rng, x0, y0, doors):
        tpl = rng.choice(TEMPLATES)
        flip = rng.random() < 0.5
        cells = [[('2' if ch == '#' else '1' if ch == '.' else rng.choice('12'))
                  for ch in (row[::-1] if flip else row)] for row in tpl]
        # Doors: 3 tall at the side, cleared one column in so nothing blocks them.
        for side, cols in (('L', (0, 1)), ('R', (ROOM_W - 1, ROOM_W - 2))):
            if side in doors:
                for x in cols:
                    for y in (2, 3, 4):
                        cells[y][x] = '1'
        # Holes: 2 wide in the middle, with a clear shaft through the room.
        if 'B' in doors:
            for x in (3, 4):
                for y in (3, 4, 5):
                    cells[y][x] = '1'
        if 'T' in doors:
            for x in (3, 4):
                for y in (0, 1, 2):
                    cells[y][x] = '1'
        for y, row in enumerate(cells):
            for x, ch in enumerate(row):
                self.grid.grid[y0 + y][x0 + x] = ch
