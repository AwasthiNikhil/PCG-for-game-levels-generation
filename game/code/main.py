from settings import *
from levelloader import *
from sprites import *
from groups import *
from support import *

class Game():
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        pygame.display.set_caption('Game')
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()        
        self.exit_sprite = pygame.sprite.Group()        
        self.collectible_sprite = pygame.sprite.Group()       
                
        self.current_level_url = (
            f'http://127.0.0.1:5000/generate/{LEVEL_TYPE}?x={QUERY_PARAMS["WIDTH"]}'
            f'&y={QUERY_PARAMS["HEIGHT"]}'
            f'&seed={QUERY_PARAMS["SEED"]}'
            f'&scale={QUERY_PARAMS["SCALE"]}'
            f'&min_leaf_size={QUERY_PARAMS["MIN_LEAF_SIZE"]}'
            f'&max_leaf_size={QUERY_PARAMS["MAX_LEAF_SIZE"]}'
            f'&wall_probability={QUERY_PARAMS["WALL_PROBABILITY"]}'
            f'&threshold={QUERY_PARAMS["THRESHOLD"]}'
            f'&min_room_size={QUERY_PARAMS["MIN_ROOM_SIZE"]}'
            f'&max_rooms={QUERY_PARAMS["MAX_ROOMS"]}'
            f'&iterations={QUERY_PARAMS["ITERATIONS"]}'
        )

        # load game
        self.load_assets()
        self.setup()
        self.log()   

    def load_assets(self):
        self.player_frames = import_folder('images','player')
    
    def setup(self):
        # self.level_loader = LevelLoader('../output')
        self.level_loader = LevelLoader(self.current_level_url)
        self.level_data = self.level_loader.get_grid()
        
        for y, row in enumerate(self.level_data):
            for x, block in enumerate(row):
                block_info = BLOCKS.get(block)
                if block_info:  # Ensure it's a valid block
                    color = pygame.Color(block_info['color'])
                    image =  pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))    
                    image.fill(color)
                    Sprite((x * BLOCK_SIZE, y * BLOCK_SIZE), image, self.all_sprites)
        
        for y, row in enumerate(self.level_data):
            for x, block in enumerate(row):
                block_info = BLOCKS.get(block)
                if block_info and block_info['name'] == 'wall':
                    color = pygame.Color(block_info['color'])
                    image =  pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))    
                    image.fill(color)
                    CollisionSprite((x * BLOCK_SIZE, y * BLOCK_SIZE), image, self.collision_sprites)
                                
        self.exit_door = ExitDoor(self.get_exit_spawnable_position(), (self.all_sprites, self.exit_sprite))
        self.exit_key = Key(self.get_item_spawnable_position(), (self.all_sprites, self.collectible_sprite))
        self.player = Player(self.get_player_spawnable_position(), self.all_sprites, self.collision_sprites, self.exit_sprite, self.collectible_sprite, self.player_frames)    
    
    def log(self):
        print('Current Level Data:')
        for param in QUERY_PARAMS:
            print(f'{param}: {QUERY_PARAMS[param]}')
    
        print('---------------------------------------')
        print('Player: ', self.get_player_spawnable_position())
        print('Key', self.get_item_spawnable_position())
        print('Exit', self.get_exit_spawnable_position())
    
    def get_player_spawnable_position(self):
        for y in range(len(self.level_data) - 1):  
            for x in range(len(self.level_data[y]) - 1): 
                if (self.level_data[y][x] == 1 and
                    self.level_data[y][x + 1] == 1 and
                    self.level_data[y + 1][x] == 1 and
                    self.level_data[y + 1][x + 1] == 1):
                    # Return the top-left corner of the found 2x2 area
                    return (x*BLOCK_SIZE, y*BLOCK_SIZE)
        # Return None if no spawnable position was found
        return None
    
    def get_exit_spawnable_position(self):
        potential_positions = []
        for y in range(len(self.level_data) - 1):  
            for x in range(len(self.level_data[y])):
                if (self.level_data[y][x] == 1 and self.level_data[y + 1][x] == 1):
                    # Store the position of the top cell of the 2x1 space
                    potential_positions.append((x*BLOCK_SIZE, y*BLOCK_SIZE))
        if potential_positions:
            return choice(potential_positions)
    
    def get_item_spawnable_position(self):
        potential_positions = []
        for y in range(len(self.level_data)): 
            for x in range(len(self.level_data[y])):
                if self.level_data[y][x] == 1:  # Check if the cell is a floor
                    # Store the position of the cell
                    potential_positions.append((x * BLOCK_SIZE, y * BLOCK_SIZE))
        
        if potential_positions:
            # Create a list of weights (for simplicity, all weights are equal)
            weights = [1] * len(potential_positions)
            return choices(potential_positions, weights=weights, k=1)[0]  # Select one position based on weights
        return None  # Return None if no spawnable position was found
        
    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            # update
            self.display_surface.fill(BLOCKS[1]['color'])  
            self.all_sprites.update(dt) 
                
            # draw
            self.all_sprites.draw(self.player.rect.center)
            pygame.display.update()
            
            
        
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
