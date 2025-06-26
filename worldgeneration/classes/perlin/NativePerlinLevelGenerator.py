import math
import random
from ..settings import *

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
    def __init__(self, grid, scale=2.0, threshold=0.0, min_room_size=4):
        self.grid = grid
        self.scale = scale
        self.threshold = threshold
        self.min_room_size = min_room_size  # Minimum size to consider converting to walls

    def generate(self, seed=None):
        if seed is not None:
            random.seed(seed)
        else:
            seed = random.randint(0, 1000)
            random.seed(seed)
            
        print(f'seed: {seed}')
        grad_table = generate_gradient_table(self.grid.width, self.grid.height)

        # Generate initial grid
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                nx = x / self.scale
                ny = y / self.scale
                n = perlin(nx, ny, grad_table)
                self.grid.grid[y][x] = WALL_CHAR if n < self.threshold else FLOOR_CHAR

        # Generate boundaries
        for x in range(self.grid.width):
            self.grid.grid[0][x] = WALL_CHAR          # Top boundary
            self.grid.grid[self.grid.height-1][x] = WALL_CHAR  # Bottom boundary
        for y in range(self.grid.height):
            self.grid.grid[y][0] = WALL_CHAR          # Left boundary
            self.grid.grid[y][self.grid.width-1] = WALL_CHAR  # Right boundary

        # Remove diagonal blockers
        self.remove_diagonal_blockers()

        # Break enclosures
        self.break_enclosures()

    def break_enclosures(self):
        """Find and minimally disrupt enclosed areas by strategically removing walls"""
        visited = [[False]*self.grid.width for _ in range(self.grid.height)]
        
        for y in range(1, self.grid.height-1):
            for x in range(1, self.grid.width-1):
                if not visited[y][x] and self.grid.grid[y][x] == FLOOR_CHAR:
                    # Get all connected floor tiles (room)
                    room = self.flood_fill(y, x, visited)
                    
                    # Check if room is enclosed
                    if self.is_enclosed(room):
                        self.find_and_break_wall(room)

    def remove_diagonal_blockers(self):
        """Remove wall configurations that would block diagonal movement"""
        for y in range(1, self.grid.height-1):
            for x in range(1, self.grid.width-1):
                if self.grid.grid[y][x] == WALL_CHAR:
                    # Check for 8-directional patterns that would block movement
                    if (self.is_solid_diagonal(y, x) or 
                        self.is_solid_one_way_blocker(y, x)):
                        self.grid.grid[y][x] = FLOOR_CHAR

    def is_solid_diagonal(self, y, x):
        """Check for fully enclosed diagonal blocks"""
        return ((self.grid.grid[y-1][x] == WALL_CHAR and 
                 self.grid.grid[y][x-1] == WALL_CHAR and 
                 self.grid.grid[y-1][x-1] == FLOOR_CHAR) or
                (self.grid.grid[y+1][x] == WALL_CHAR and 
                 self.grid.grid[y][x+1] == WALL_CHAR and 
                 self.grid.grid[y+1][x+1] == FLOOR_CHAR) or
                (self.grid.grid[y+1][x] == WALL_CHAR and 
                 self.grid.grid[y][x-1] == WALL_CHAR and 
                 self.grid.grid[y+1][x-1] == FLOOR_CHAR) or
                (self.grid.grid[y-1][x] == WALL_CHAR and 
                 self.grid.grid[y][x+1] == WALL_CHAR and 
                 self.grid.grid[y-1][x+1] == FLOOR_CHAR))

    def is_solid_one_way_blocker(self, y, x):
        """Check for walls that would create one-directional barriers"""
        return ((self.grid.grid[y-1][x] == FLOOR_CHAR and 
                 self.grid.grid[y][x+1] == FLOOR_CHAR and 
                 self.grid.grid[y-1][x+1] == WALL_CHAR) or
                (self.grid.grid[y+1][x] == FLOOR_CHAR and 
                 self.grid.grid[y][x-1] == FLOOR_CHAR and 
                 self.grid.grid[y+1][x-1] == WALL_CHAR) or
                (self.grid.grid[y+1][x] == FLOOR_CHAR and 
                 self.grid.grid[y][x+1] == FLOOR_CHAR and 
                 self.grid.grid[y+1][x+1] == WALL_CHAR) or
                (self.grid.grid[y-1][x] == FLOOR_CHAR and 
                 self.grid.grid[y][x-1] == FLOOR_CHAR and 
                 self.grid.grid[y-1][x-1] == WALL_CHAR))

    def flood_fill(self, y, x, visited):
        """Standard flood fill to get connected floor tiles"""
        stack = [(y, x)]
        room = set()
        
        while stack:
            cy, cx = stack.pop()
            if visited[cy][cx]:
                continue
                
            visited[cy][cx] = True
            room.add((cy, cx))
            
            for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                ny, nx = cy + dy, cx + dx
                if (1 <= ny < self.grid.height-1 and 
                    1 <= nx < self.grid.width-1 and 
                    not visited[ny][nx] and 
                    self.grid.grid[ny][nx] == FLOOR_CHAR):
                    stack.append((ny, nx))
        return room

    def is_enclosed(self, room):
        """Check if an area is completely walled off"""
        for y, x in room:
            # If any floor tile touches the boundary, not enclosed
            if y == 1 or y == self.grid.height-2 or x == 1 or x == self.grid.width-2:
                return False
            # If any neighbor is floor not in this room, not enclosed
            for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                if self.grid.grid[y+dy][x+dx] == FLOOR_CHAR and (y+dy, x+dx) not in room:
                    return False
        return True

    def find_and_break_wall(self, room):
        """Find optimal wall to convert to floor to break enclosure"""
        # First try to connect to nearest edge
        for y, x in sorted(room, key=lambda p: min(p[0], self.grid.height-p[0], p[1], self.grid.width-p[1])):
            for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                if self.grid.grid[y+dy][x+dx] == WALL_CHAR and (y+dy, x+dx) not in room:
                    if 1 <= y+dy < self.grid.height-1 and 1 <= x+dx < self.grid.width-1:
                        self.grid.grid[y+dy][x+dx] = FLOOR_CHAR
                        return  # Exit after making one change
        
        # If no edge found, just break any wall
        for y, x in room:
            for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                if self.grid.grid[y+dy][x+dx] == WALL_CHAR:
                    self.grid.grid[y+dy][x+dx] = FLOOR_CHAR
                    return

