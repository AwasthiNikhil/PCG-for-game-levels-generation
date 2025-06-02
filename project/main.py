from classes.Grid import Grid
from classes.LevelPostProcessor import LevelPostProcessor
from classes.random.RandomLevelGenerator import RandomLevelGenerator
from classes.perlin.NativePerlinLevelGenerator import NativePerlinLevelGenerator
from classes.simplex.SimplexLevelGenerator import SimplexLevelGenerator
from classes.cellularautomata.CellularAutomataLevelGenerator import CellularAutomataLevelGenerator
from classes.bsp.BSPLevelGenerator import BSPLevelGenerator
from classes.wfc.WFCLevelGenerator import WFCLevelGenerator
from classes.graph.GraphLevelGenerator import GraphLevelGenerator

# delimeter for html parsing, remove later
print("<<<")

grid = Grid(100,100)

types_of_levels_string = """
1. Random Generation
2. Perlin
3. Simplex
4. Cellular Automata
5. Binary Space Partitioning (BSP)
6. Wave Function Collapse (WFC)
7. Graph-Based Generation
"""

level_type = input(types_of_levels_string)

match level_type:
    case '1':
        level_generator = RandomLevelGenerator(grid)
    case '2':
        level_generator = NativePerlinLevelGenerator(grid,scale=5)
    case '3':
        level_generator = SimplexLevelGenerator(grid)
    case '4':
        level_generator = CellularAutomataLevelGenerator(grid)
    case '5':
        level_generator = BSPLevelGenerator(grid, min_leaf_size=8, max_leaf_size=15)
    case '6':
        level_generator = WFCLevelGenerator(grid)
    case '7':
        level_generator = GraphLevelGenerator(grid)
    case '8':
       print()
    case _:
        print('No type selected. Execution completed.')

level_generator.generate()

match level_type:
    case '1':   
        post_processor = LevelPostProcessor(grid)
        post_processor.remove_isolated_walls()
    case '_':
        pass


# delimeter for html parsing, remove later        
print(">>>")
grid.display()
