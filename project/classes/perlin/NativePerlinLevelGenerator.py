
import math
import random

def fade(t):
    """Smoothstep function to ease the interpolation"""
    return t * t * t * (t * (t * 6 - 15) + 10)

def lerp(a, b, t):
    """Linear interpolation"""
    return a + t * (b - a)

def dot_grid_gradient(ix, iy, x, y, grad_table):
    """Compute dot product between gradient and distance vector"""
    dx = x - ix
    dy = y - iy

    gradient = grad_table[iy % len(grad_table)][ix % len(grad_table[0])]
    return dx * gradient[0] + dy * gradient[1]

def generate_gradient_table(width, height):
    """Generate pseudo-random 2D unit vectors (gradients) at grid points"""
    table = []
    for y in range(height + 1):
        row = []
        for x in range(width + 1):
            angle = random.uniform(0, 2 * math.pi)
            row.append((math.cos(angle), math.sin(angle)))
        table.append(row)
    return table

def perlin(x, y, grad_table):
    # Grid cell coordinates
    x0 = int(math.floor(x))
    x1 = x0 + 1
    y0 = int(math.floor(y))
    y1 = y0 + 1

    # Relative x, y in cell
    sx = x - x0
    sy = y - y0

    # Dot products at each corner
    n00 = dot_grid_gradient(x0, y0, x, y, grad_table)
    n10 = dot_grid_gradient(x1, y0, x, y, grad_table)
    n01 = dot_grid_gradient(x0, y1, x, y, grad_table)
    n11 = dot_grid_gradient(x1, y1, x, y, grad_table)

    # Interpolate using fade
    u = fade(sx)
    v = fade(sy)

    nx0 = lerp(n00, n10, u)
    nx1 = lerp(n01, n11, u)
    nxy = lerp(nx0, nx1, v)

    return nxy  # Typically in range [-1, 1]



class NativePerlinLevelGenerator:
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
            seed = random.randint(0,1000)
            random.seed(seed)
            
        
        print(f'seed:{seed}')
        grad_table = generate_gradient_table(self.grid.width, self.grid.height)

        for y in range(self.grid.height):
            for x in range(self.grid.width):
                nx = x / self.scale
                ny = y / self.scale
                n = perlin(nx, ny, grad_table)

                if n < self.threshold:
                    self.grid.grid[y][x] = self.wall_char
                else:
                    self.grid.grid[y][x] = self.floor_char
