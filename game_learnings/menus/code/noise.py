import math
import random

# Perlin Noise Implementation
class PerlinNoise:
    def __init__(self, seed=None):
        self.seed = seed or random.randint(0, 100)
        self.gradients = {}
        self.permutation = list(range(256))
        random.shuffle(self.permutation)
        self.permutation += self.permutation

    def dot_grid_gradient(self, ix, iy, x, y):
        # Generate a random gradient vector
        if (ix, iy) not in self.gradients:
            angle = random.uniform(0, 2 * math.pi)
            self.gradients[(ix, iy)] = (math.cos(angle), math.sin(angle))
        gradient = self.gradients[(ix, iy)]

        # Compute the distance vector
        dx, dy = x - ix, y - iy

        # Compute the dot product
        return dx * gradient[0] + dy * gradient[1]

    def fade(self, t):
        # Fade function for smooth interpolation
        return t * t * t * (t * (t * 6 - 15) + 10)

    def lerp(self, a, b, t):
        # Linear interpolation
        return a + t * (b - a)

    def noise(self, x, y):
        # Determine grid cell coordinates
        x0 = int(x) & 255
        x1 = (x0 + 1) & 255
        y0 = int(y) & 255
        y1 = (y0 + 1) & 255

        # Determine interpolation weights
        sx = self.fade(x - int(x))
        sy = self.fade(y - int(y))

        # Interpolate between grid point gradients
        n0 = self.dot_grid_gradient(x0, y0, x, y)
        n1 = self.dot_grid_gradient(x1, y0, x, y)
        ix0 = self.lerp(n0, n1, sx)

        n0 = self.dot_grid_gradient(x0, y1, x, y)
        n1 = self.dot_grid_gradient(x1, y1, x, y)
        ix1 = self.lerp(n0, n1, sx)

        return self.lerp(ix0, ix1, sy)

# Simplex Noise Implementation
class SimplexNoise:
    def __init__(self, seed=None):
        self.seed = seed or random.randint(0, 100)
        self.grad3 = [(1, 1, 0), (-1, 1, 0), (1, -1, 0), (-1, -1, 0),
                      (1, 0, 1), (-1, 0, 1), (1, 0, -1), (-1, 0, -1),
                      (0, 1, 1), (0, -1, 1), (0, 1, -1), (0, -1, -1)]
        self.permutation = list(range(256))
        random.shuffle(self.permutation)
        self.permutation += self.permutation

    def dot(self, g, x, y):
        return g[0] * x + g[1] * y

    def noise(self, xin, yin):
        # Skewing and unskewing factors
        F2 = 0.5 * (math.sqrt(3) - 1)
        G2 = (3 - math.sqrt(3)) / 6

        # Skew the input space to determine which simplex cell we're in
        s = (xin + yin) * F2
        i = math.floor(xin + s)
        j = math.floor(yin + s)

        t = (i + j) * G2
        X0 = i - t
        Y0 = j - t
        x0 = xin - X0
        y0 = yin - Y0

        # Determine which simplex we are in
        if x0 > y0:
            i1, j1 = 1, 0
        else:
            i1, j1 = 0, 1

        x1 = x0 - i1 + G2
        y1 = y0 - j1 + G2
        x2 = x0 - 1 + 2 * G2
        y2 = y0 - 1 + 2 * G2

        # Hash the corners of the simplex
        ii = i & 255
        jj = j & 255
        g0 = self.grad3[self.permutation[ii + self.permutation[jj]] % 12]
        g1 = self.grad3[self.permutation[ii + i1 + self.permutation[jj + j1]] % 12]
        g2 = self.grad3[self.permutation[ii + 1 + self.permutation[jj + 1]] % 12]

        # Calculate the contribution from the three corners
        t0 = 0.5 - x0 * x0 - y0 * y0
        n0 = t0 * t0 * self.dot(g0, x0, y0) if t0 > 0 else 0

        t1 = 0.5 - x1 * x1 - y1 * y1
        n1 = t1 * t1 * self.dot(g1, x1, y1) if t1 > 0 else 0

        t2 = 0.5 - x2 * x2 - y2 * y2
        n2 = t2 * t2 * self.dot(g2, x2, y2) if t2 > 0 else 0

        # Add contributions and scale the result
        return 70 * (n0 + n1 + n2)
    