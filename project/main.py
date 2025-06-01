from classes.Grid import Grid
from classes.LevelPostProcessor import LevelPostProcessor
from classes.random.RandomLevelGenerator import RandomLevelGenerator
from classes.perlin.NativePerlinLevelGenerator import NativePerlinLevelGenerator

# delimeter for html parsing, remove later
print("<<<")

grid = Grid(60,48)


types_of_levels_string = """
1. Random Generation
2. Perlin
3. Simplex
4. Cellular Automata
5. Binary Space Partitioning (BSP)
6. Wave Function Collapse (WFC)
7. Graph-Based Generation
8. Markov Chains / Probabilistic Models
9. Evolutionary Algorithms / Genetic Algorithms
"""

level_type = input(types_of_levels_string)


match level_type:
    case '1':
        # print('1 selected\n')     
        level_generator = RandomLevelGenerator(grid)
        # provide user with slider to change wall/floor ratio or increase difficulty with each level
    case '2':
        level_generator = NativePerlinLevelGenerator(grid)

level_generator.generate()

match level_type:
    case '1':   
        post_processor = LevelPostProcessor(grid)
        post_processor.remove_isolated_walls()
    # case '2':   
    #     post_processor = LevelPostProcessor(grid)
    #     post_processor.remove_isolated_walls()
        
        
# delimeter for html parsing, remove later        
print(">>>")
grid.display()
