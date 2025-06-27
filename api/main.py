from flask import Flask, request, Response
from io import StringIO
import sys

from classes.Grid import Grid
from classes.LevelPostProcessor import LevelPostProcessor
from classes.random.RandomLevelGenerator import RandomLevelGenerator
from classes.perlin.NativePerlinLevelGenerator import NativePerlinLevelGenerator
from classes.simplex.SimplexLevelGenerator import SimplexLevelGenerator
from classes.cellularautomata.CellularAutomataLevelGenerator import CellularAutomataLevelGenerator
from classes.bsp.BSPLevelGenerator import BSPLevelGenerator
from classes.wfc.WFCLevelGenerator import WFCLevelGenerator
from classes.graph.GraphLevelGenerator import GraphLevelGenerator

app = Flask(__name__)

@app.route('/generate/<int:level_type>', methods=['GET'])
def generate_level(level_type):
    # Redirect print output
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    print("<<<")  # Start delimiter
    
    # --- Parse optional query parameters ---

    def safe_int(val, default):
        try:
            return int(val)
        except (TypeError, ValueError):
            return default

    def safe_float(val, default):
        try:
            return float(val)
        except (TypeError, ValueError):
            return default

    # --- Safely parse query parameters ---
    width = safe_int(request.args.get('x'), 25)
    height = safe_int(request.args.get('y'), 25)
    seed = request.args.get('seed', None)
    scale = safe_float(request.args.get('scale'), 2.0)
    min_leaf_size = safe_int(request.args.get('min_leaf_size'), 8)
    max_leaf_size = safe_int(request.args.get('max_leaf_size'), 15)
    wall_probability = safe_float(request.args.get('wall_probability'), 0.45)
    threshold = safe_int(request.args.get('threshold'), 4)
    min_room_size = safe_int(request.args.get('min_room_size'), 3)
    max_rooms = safe_int(request.args.get('max_rooms'), 15)
    iterations = safe_int(request.args.get('iterations'), 1)
    
    grid = Grid(width, height)

    level_generator = None

    if level_type == 1:
        level_generator = RandomLevelGenerator(grid=grid)
    elif level_type == 2:
        # level_generator = NativePerlinLevelGenerator(grid=grid, scale=scale, threshold=threshold, min_room_size=min_room_size)
        level_generator = NativePerlinLevelGenerator(grid=grid)
    elif level_type == 3:
        # level_generator = SimplexLevelGenerator(grid=grid, threshold=threshold, scale=scale)
        level_generator = SimplexLevelGenerator(grid=grid)
    elif level_type == 4:
        # level_generator = CellularAutomataLevelGenerator(grid=grid, wall_probability=wall_probability, iterations=iterations)
        level_generator = CellularAutomataLevelGenerator(grid=grid,  iterations=iterations)
    elif level_type == 5:
        level_generator = BSPLevelGenerator(grid, min_leaf_size=min_leaf_size, max_leaf_size=max_leaf_size)
    elif level_type == 6:
        level_generator = GraphLevelGenerator(grid, max_rooms=max_rooms, room_min_size=min_room_size, room_max_size=max_rooms)
    else:
        print("No type selected. Execution completed.")
        print(">>>")
        sys.stdout = old_stdout
        return Response(mystdout.getvalue(), mimetype='text/plain')

    level_generator.generate(seed= seed if seed else None)

    if level_type == 1:
        post_processor = LevelPostProcessor(grid)
        post_processor.remove_isolated_walls()

    print(">>>")  # End delimiter
    
    grid.display()

    # Reset stdout and return output
    sys.stdout = old_stdout
    print(f"Seed {seed} ")
    
    return Response(mystdout.getvalue(), mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True)
