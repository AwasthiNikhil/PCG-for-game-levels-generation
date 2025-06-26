from flask import Flask, Response
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

    grid = Grid(25, 25)

    level_generator = None

    if level_type == 1:
        level_generator = RandomLevelGenerator(grid)
    elif level_type == 2:
        level_generator = NativePerlinLevelGenerator(grid, scale=2)
    elif level_type == 3:
        level_generator = SimplexLevelGenerator(grid)
    elif level_type == 4:
        level_generator = CellularAutomataLevelGenerator(grid)
    elif level_type == 5:
        level_generator = BSPLevelGenerator(grid, min_leaf_size=8, max_leaf_size=15)
    elif level_type == 6:
        level_generator = GraphLevelGenerator(grid)
    else:
        print("No type selected. Execution completed.")
        print(">>>")
        sys.stdout = old_stdout
        return Response(mystdout.getvalue(), mimetype='text/plain')

    level_generator.generate()

    if level_type == 1:
        post_processor = LevelPostProcessor(grid)
        post_processor.remove_isolated_walls()

    print(">>>")  # End delimiter
    grid.display()

    # Reset stdout and return output
    sys.stdout = old_stdout
    return Response(mystdout.getvalue(), mimetype='text/plain')


if __name__ == '__main__':
    app.run(debug=True)
