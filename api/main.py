from flask import Flask, request, Response, jsonify
from io import StringIO
import sys
from database.NetworkManager import NetworkManager
from classes.Grid import Grid
from classes.LevelPostProcessor import LevelPostProcessor
from classes.random.RandomLevelGenerator import RandomLevelGenerator
from classes.perlin.NativePerlinLevelGenerator import NativePerlinLevelGenerator
from classes.simplex.SimplexLevelGenerator import SimplexLevelGenerator
from classes.cellularautomata.CellularAutomataLevelGenerator import CellularAutomataLevelGenerator
from classes.bsp.BSPLevelGenerator import BSPLevelGenerator
from classes.wfc.WFCLevelGenerator import WFCLevelGenerator
from classes.graph.GraphLevelGenerator import GraphLevelGenerator
from classes.transformer.leveltransformergenerator import LevelTransformerGenerator

app = Flask(__name__)

@app.route('/generate/<int:level_type>', methods=['GET'])
def generate_level(level_type):
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
    wall_probability = safe_float(request.args.get('wall_probability'), 0.45)/100
    threshold = safe_float(request.args.get('threshold'), 0.0) /100
    min_room_size = safe_int(request.args.get('min_room_size'), 3)
    max_rooms = safe_int(request.args.get('max_rooms'), 15)
    iterations = safe_int(request.args.get('iterations'), 1)
    
    # Redirect print output
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    print("<<<")  # Start delimiter
    grid = Grid(width, height)

    level_generator = None

    if level_type == 1:
        level_generator = RandomLevelGenerator(grid=grid, wall_prob=wall_probability)
    elif level_type == 2:
        level_generator = NativePerlinLevelGenerator(grid=grid, threshold= threshold)
    elif level_type == 3:
        # level_generator = SimplexLevelGenerator(grid=grid, threshold=threshold, scale=scale)
        level_generator = SimplexLevelGenerator(grid=grid)
    elif level_type == 4:
        # level_generator = CellularAutomataLevelGenerator(grid=grid, wall_probability=wall_probability, iterations=iterations)
        level_generator = CellularAutomataLevelGenerator(grid=grid, wall_probability=wall_probability, iterations=iterations)
    elif level_type == 5:
        level_generator = BSPLevelGenerator(grid, min_leaf_size=min_leaf_size, max_leaf_size=max_leaf_size)
    elif level_type == 6:
        level_generator = GraphLevelGenerator(grid, max_rooms=max_rooms, min_room_size=min_room_size, max_room_size=max_rooms)
    elif level_type == 7:
        level_generator = LevelTransformerGenerator(grid, width=width, height=height)
    else:
        print("No type selected. Execution completed.")
        print(">>>")
        sys.stdout = old_stdout
        return Response(mystdout.getvalue(), mimetype='text/plain')

    level_generator.generate(seed= seed if seed else None)

    if level_type == 1:
        post_processor = LevelPostProcessor(grid)
        post_processor.remove_isolated_walls()

    print(">>>")  
    
    grid.display()

    # Reset stdout and return output
    sys.stdout = old_stdout
    print(f"Seed {seed} ")
    
    return Response(mystdout.getvalue(), mimetype='text/plain')

@app.route('/level/<int:user>',methods=['GET'])
def get_user_level(user):
    db = NetworkManager()
    query = 'SELECT level, completed FROM public.player_levels WHERE user_id = %s'
    user_level = db.fetch_all(query, (user,))
    db.close()
    return jsonify(min([level for level, completed in user_level if not completed]))

@app.route('/login',methods=['GET'])
def login_or_register():
    username = request.args.get('username')
    password = request.args.get('password')
    db = NetworkManager()    
    response = db.login_or_register_user(username, password)
    db.close()
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
