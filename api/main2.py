import os
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
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
from classes.rooms.RoomLevelGenerator import RoomLevelGenerator
from classes.transformer.TileGPTLevelGenerator import TileGPTLevelGenerator
from placement import plan_route, good_enough
from platformize import platformize

app = Flask(__name__)
CORS(app)

@app.route('/generate/<int:level_type>', methods=['GET'])
def generate_level(level_type):
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

    # Parse query parameters
    width = safe_int(request.args.get('x'), 25)
    height = safe_int(request.args.get('y'), 25)
    seed = request.args.get('seed', None)
    scale = safe_float(request.args.get('scale'), 6.0)  # simplex feature size; 2 is near-static noise
    min_leaf_size = safe_int(request.args.get('min_leaf_size'), 8)
    max_leaf_size = safe_int(request.args.get('max_leaf_size'), 15)
    wall_probability = safe_float(request.args.get('wall_probability'), 45) / 100  # percent
    threshold = safe_float(request.args.get('threshold'), 0.0) / 100
    min_room_size = safe_int(request.args.get('min_room_size'), 3)
    max_rooms = safe_int(request.args.get('max_rooms'), 15)
    max_room_size = safe_int(request.args.get('max_room_size'), 8)
    iterations = safe_int(request.args.get('iterations'), 1)
    use_platformize = request.args.get('platformize', '1') != '0'

    params = dict(width=width, height=height, scale=scale, min_leaf_size=min_leaf_size, max_leaf_size=max_leaf_size,
                  wall_probability=wall_probability, threshold=threshold, min_room_size=min_room_size,
                  max_rooms=max_rooms, max_room_size=max_room_size, iterations=iterations,
                  platformize=use_platformize)
    if level_type not in GENERATORS:
        return jsonify({"error": "Invalid level type"}), 400

    # Generate, then place start/key/exit on a reachable route. Poor levels
    # (little reachable space or a short route) are regenerated; the best of
    # the attempts is kept. The transformer is slow, so it gets fewer tries.
    base_seed = seed or str(random.randrange(10 ** 9))
    tries = 2 if level_type in SLOW else MAX_TRIES
    best = None
    for attempt in range(tries):
        attempt_seed = base_seed if attempt == 0 else f"{base_seed}-{attempt}"
        grid_array = build_grid(level_type, params, attempt_seed)
        plan = plan_route(grid_array)
        score = (good_enough(plan), plan["route"] * plan["reach_share"]) if plan else (False, -1)
        if best is None or score > best[0]:
            best = (score, grid_array, plan, attempt_seed, attempt + 1)
        if score[0]:
            break
    _, grid_array, plan, used_seed, attempts = best

    return jsonify({
        "metadata": {
            "seed": used_seed,
            "level_type": level_type,
            "width": width,
            "height": height,
            "attempts": attempts,
            "route": plan["route"] if plan else None,
            "reach_share": plan["reach_share"] if plan else None,
        },
        "grid": grid_array,
        # [x, y] cells; null if the level has nowhere to stand (the game falls back)
        "start": plan["start"] if plan else None,
        "key": plan["key"] if plan else None,
        "exit": plan["exit"] if plan else None,
    })


MAX_TRIES = 5
SLOW = {7, 9, 10}  # model-based generators
GENERATORS = {
    1: lambda g, p: RandomLevelGenerator(grid=g, wall_prob=p['wall_probability']),
    2: lambda g, p: NativePerlinLevelGenerator(grid=g, threshold=p['threshold']),
    3: lambda g, p: SimplexLevelGenerator(grid=g, scale=p['scale'], threshold=p['threshold']),
    4: lambda g, p: CellularAutomataLevelGenerator(grid=g, wall_probability=p['wall_probability'], iterations=p['iterations']),
    5: lambda g, p: BSPLevelGenerator(g, min_leaf_size=p['min_leaf_size'], max_leaf_size=p['max_leaf_size']),
    6: lambda g, p: GraphLevelGenerator(g, max_rooms=p['max_rooms'], min_room_size=p['min_room_size'], max_room_size=p['max_room_size']),
    7: lambda g, p: LevelTransformerGenerator(g, width=p['width'], height=p['height']),
    8: lambda g, p: RoomLevelGenerator(g),
    9: lambda g, p: TileGPTLevelGenerator(g, 'mario'),       # trained on VGLC Super Mario Bros
    10: lambda g, p: TileGPTLevelGenerator(g, 'loderunner'), # retrained Lode Runner, for comparison
}


def build_grid(level_type, params, seed):
    grid = Grid(params['width'], params['height'])
    GENERATORS[level_type](grid, params).generate(seed=seed)
    if level_type == 1:
        LevelPostProcessor(grid).remove_isolated_walls()
    cells = [[grid.get(x, y) for x in range(grid.width)] for y in range(grid.height)]
    # The top-down style generators and the Mario model get ledges, doors and
    # ceiling holes so they work as platformer levels (rooms are built for it;
    # the Lode Runner models are left as generated).
    if params['platformize'] and level_type in PLATFORMIZED:
        platformize(cells, random.Random(f"{seed}:platformize"))
    return cells


PLATFORMIZED = {1, 2, 3, 4, 5, 6, 9}  # 9: Mario's sealed ground lines need joining


if __name__ == '__main__':
    # 5055, not Flask's default 5000: macOS uses 5000 for AirPlay.
    app.run(host='127.0.0.1', port=int(os.environ.get('PORT', 5055)))
