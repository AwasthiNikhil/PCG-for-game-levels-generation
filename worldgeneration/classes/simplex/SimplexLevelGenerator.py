import math
import random

# constants START
SQRT3 = math.sqrt(3.0)
F2 = 0.5 * (SQRT3 - 1.0)
G2 = (3.0 - SQRT3) / 6.0

GRADIENTS = [
    (1,1), (-1,1), (1,-1), (-1,-1),
    (1,0), (-1,0), (0,1), (0,-1)
]
# constants END

def generate_permutation_table(seed=None):
    if seed is not None:
        random.seed(seed)
    p = list(range(256))
    random.shuffle(p)
    return p * 2  # Repeat to avoid overflow

def dot(g, x, y):
    return g[0]*x + g[1]*y

def simplex_noise_2d(xin, yin, perm):
    s = (xin + yin) * F2
    i = int(xin + s)
    j = int(yin + s)
    t = (i + j) * G2
    X0 = i - t
    Y0 = j - t
    x0 = xin - X0
    y0 = yin - Y0

    if x0 > y0:
        i1, j1 = 1, 0
    else:
        i1, j1 = 0, 1

    x1 = x0 - i1 + G2
    y1 = y0 - j1 + G2
    x2 = x0 - 1.0 + 2.0 * G2
    y2 = y0 - 1.0 + 2.0 * G2

    ii = i & 255
    jj = j & 255
    gi0 = perm[ii + perm[jj]] % 8
    gi1 = perm[ii + i1 + perm[jj + j1]] % 8
    gi2 = perm[ii + 1 + perm[jj + 1]] % 8

    t0 = 0.5 - x0*x0 - y0*y0
    n0 = 0
    if t0 > 0:
        t0 *= t0
        n0 = t0 * t0 * dot(GRADIENTS[gi0], x0, y0)

    t1 = 0.5 - x1*x1 - y1*y1
    n1 = 0
    if t1 > 0:
        t1 *= t1
        n1 = t1 * t1 * dot(GRADIENTS[gi1], x1, y1)

    t2 = 0.5 - x2*x2 - y2*y2
    n2 = 0
    if t2 > 0:
        t2 *= t2
        n2 = t2 * t2 * dot(GRADIENTS[gi2], x2, y2)

    return 70.0 * (n0 + n1 + n2)


class SimplexLevelGenerator:
    def __init__(self, grid, scale=2.0, threshold=0.0):
        self.grid = grid
        self.scale = scale
        self.threshold = threshold
        self.floor_char = '1'
        self.wall_char = '2'
    
    def generate(self, seed=None):
        if seed is not None:
            random.seed(seed)
        else:
            seed = random.randint(0, 1000)
            random.seed(seed)

        print(f'seed:{seed}')
        perm = generate_permutation_table(seed)

        for y in range(self.grid.height):
            for x in range(self.grid.width):
                nx = x / self.scale
                ny = y / self.scale
                n = simplex_noise_2d(nx, ny, perm)

                if n < self.threshold:
                    self.grid.grid[y][x] = self.wall_char
                else:
                    self.grid.grid[y][x] = self.floor_char