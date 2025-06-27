from settings import *
from levelloader import *
from sprites import *
from groups import *
from support import *
from timer import Timer

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
        
        self.level_width = QUERY_PARAMS["WIDTH"] 
        self.level_height = QUERY_PARAMS["HEIGHT"] 
        
        self.current_level_url = (
            f'http://127.0.0.1:5000/generate/{LEVEL_TYPE}?x={self.level_width}'
            f'&y={self.level_height}'
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
        
        # gui logger
        self.gui_logger = pygame.Surface((500,275), pygame.SRCALPHA)
        self.gui_logger_rect = self.gui_logger.get_rect(topright=(SCREEN_WIDTH-10, 10))
        self.gui_font = pygame.font.Font(None, 24)
        self.gui_font_big = pygame.font.Font(None, 48)
        
        # timer
        # felt cute might delete later
        self.remaining_time = 0
        self.countdown_timer = Timer(20000, func = self.countdown, autostart = True, repeat = False)
        self.timer_surface = pygame.Surface((200,50), pygame.SRCALPHA)
        self.timer_surface_rect = self.timer_surface.get_rect(midtop=(SCREEN_WIDTH/2, 10))
        self.game_over_surface = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT), pygame.SRCALPHA)
        self.game_over_surface_rect = self.game_over_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        
    def interpolate_color(self, start_color, end_color, factor):
        r = int(start_color[0] * (1 - factor) + end_color[0] * factor)
        g = int(start_color[1] * (1 - factor) + end_color[1] * factor)
        b = int(start_color[2] * (1 - factor) + end_color[2] * factor)
        return (r, g, b)
    
    def countdown(self):
        if self.remaining_time:
            # Calculate the remaining time
            remaining_time = self.countdown_timer.update()  # In milliseconds
            remaining_seconds = remaining_time // 1000  # Convert to seconds
            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60
            
            # Calculate the percentage of remaining time
            if self.countdown_timer.duration > 0:
                remaining_percentage = remaining_time / self.countdown_timer.duration
            else:
                remaining_percentage = 0

            self.timer_surface.fill((0, 0, 0, 0))  
            # Draw the background of the bar
            pygame.draw.rect(
                surface=self.timer_surface,
                color=(255, 255, 255, 50),  
                rect=(0, 0, self.timer_surface.get_width(), self.timer_surface.get_height()), 
                border_radius=10
            )

            start_color = (0, 255, 0)
            end_color = (255, 0, 0)  
            
            current_color = self.interpolate_color(start_color, end_color, 1 - remaining_percentage)
             
            bar_width = self.timer_surface.get_width() * remaining_percentage
            
            pygame.draw.rect(
                surface=self.timer_surface,
                color=current_color,  
                rect=(0, 0, bar_width, self.timer_surface.get_height()),  # Fill up to the calculated width
                border_radius=10
            )

            # Display the remaining time as text in the middle of the bar
            time_text = f"{minutes:02}:{seconds:02}"
            text_surface = self.gui_font.render(time_text, True, (0, 0, 0))  
            text_rect = text_surface.get_rect(center=self.timer_surface.get_rect().center)
            self.timer_surface.blit(text_surface, text_rect.topleft)
    
    def game_over_func(self):
        if not self.remaining_time:
            pygame.draw.rect(
                surface=self.game_over_surface,
                color=(255,255,255, 100),  
                rect=self.game_over_surface.get_rect(),  
                border_radius=10                  
            )
 
            text_surface = self.gui_font_big.render('Game Over', True, (0, 0, 0))
            self.game_over_surface.blit(text_surface, (SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            self.display_surface.blit(self.game_over_surface)
            
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
        
        # wall
        for y, row in enumerate(self.level_data):
            for x, block in enumerate(row):
                block_info = BLOCKS.get(block)
                if block_info and block_info['name'] == 'wall':
                    color = pygame.Color(block_info['color'])
                    image =  pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))    
                    image.fill(color)
                    CollisionSprite((x * BLOCK_SIZE, y * BLOCK_SIZE), image, self.collision_sprites)
                                
        self.exit_position = self.get_exit_spawnable_position()
        self.item_position = self.get_item_spawnable_position()
        self.player_position = self.get_player_spawnable_position()
        
        self.exit_door = ExitDoor(self.exit_position, (self.all_sprites, self.exit_sprite))
        self.exit_key = Key(self.item_position, (self.all_sprites, self.collectible_sprite))
        self.player = Player(self.player_position, self.all_sprites, self.collision_sprites, self.exit_sprite, self.collectible_sprite, self.player_frames, self.get_new_level)    
    
    def log(self):
        print('Current Level Data:')
        for param in QUERY_PARAMS:
            print(f'{param}: {QUERY_PARAMS[param]}')
    
        print('---------------------------------------')
        print('Player: ', self.player_position)
        print('Key', self.item_position)
        print('Exit', self.exit_position)
    
    def log_gui(self):
        pygame.draw.rect(
            surface=self.gui_logger,           # the surface you're drawing on
            color=(255,255,255, 100),              # fill color (with alpha if using SRCALPHA)
            rect=self.gui_logger.get_rect(),  # rectangle to draw
            border_radius=10                  # ← this gives rounded corners
        )

        GUI_TEXT = (
            f'URL: {self.current_level_url}',
            f'Width: {self.level_width}',  
            f'Height: {self.level_height}',
            f'Player Position: {self.player.rect.center}',
            f'Key Position: {self.item_position}',
            f'Exit Position: {self.exit_position}',
            f'Player Speed: {PLAYER_SPEED}',
            f'Player Jump: {JUMP}',
            f'Key : {"Yes" if self.player.has_key else "No"}',
        )
        for i, text in enumerate(GUI_TEXT):
            text_surface = self.gui_font.render(text, True, (0, 0, 0))
            self.gui_logger.blit(text_surface, (10, 10 + i * 30))

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
    
    def reset_query_params(self):
        return {    
            'WIDTH' : randint(20, 40),
            'HEIGHT' : randint(20, 40),
            'SEED' : randint(0, 10000),
            'SCALE' : random() * 4.0,
            'MIN_LEAF_SIZE' : randint(1, 8),
            'MAX_LEAF_SIZE' : randint(8, 15),
            'WALL_PROBABILITY' : random(),
            'THRESHOLD' : random() * 5,
            'MIN_ROOM_SIZE' : randint(0, 3),
            'MAX_ROOMS' : randint(3, 8),
            'ITERATIONS' : randint(1, 5)
        }
    
    def get_new_level(self):
        self.all_sprites.empty()
        self.collision_sprites.empty()
        self.exit_sprite.empty()
        self.collectible_sprite.empty()
        self.countdown_timer.deactivate()
        self.countdown_timer.activate()
        
        # Load new level
        new_qp = self.reset_query_params()
        self.level_width = new_qp["WIDTH"] 
        self.level_height = new_qp["HEIGHT"] 
        print(self.level_width, self.level_height)
        self.new_level_url = (
            f'http://127.0.0.1:5000/generate/{LEVEL_TYPE}?x={new_qp["WIDTH"]}'
            f'&y={new_qp["HEIGHT"]}'
            f'&seed={new_qp["SEED"]}'
            f'&scale={new_qp["SCALE"]}'
            f'&min_leaf_size={new_qp["MIN_LEAF_SIZE"]}'
            f'&max_leaf_size={new_qp["MAX_LEAF_SIZE"]}'
            f'&wall_probability={new_qp["WALL_PROBABILITY"]}'
            f'&threshold={new_qp["THRESHOLD"]}'
            f'&min_room_size={new_qp["MIN_ROOM_SIZE"]}'
            f'&max_rooms={new_qp["MAX_ROOMS"]}'
            f'&iterations={new_qp["ITERATIONS"]}'
        )

        # Todo: Make modular with setup method 
        self.level_loader = LevelLoader(self.new_level_url)
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
                                
        self.exit_position = self.get_exit_spawnable_position()
        self.item_position = self.get_item_spawnable_position()
        self.player_position = self.get_player_spawnable_position()
        
        self.exit_door = ExitDoor(self.exit_position, (self.all_sprites, self.exit_sprite))
        self.exit_key = Key(self.item_position, (self.all_sprites, self.collectible_sprite))
        self.player = Player(self.player_position, self.all_sprites, self.collision_sprites, self.exit_sprite, self.collectible_sprite, self.player_frames, self.get_new_level)    
    
        self.log()   
        
    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            # update
            self.display_surface.fill(BLOCKS[1]['color'])
            self.remaining_time = self.countdown_timer.update()//1000 if self.countdown_timer else 0
            self.all_sprites.update(dt) 
            self.countdown_timer.update()
            
            # draw
            self.all_sprites.draw(self.player.rect.center)
            
            self.log_gui()
            self.countdown()
            self.game_over_func()
            self.display_surface.blit(self.gui_logger,  self.gui_logger.get_rect(topright=(SCREEN_WIDTH - 10, 10)))
            self.display_surface.blit(self.timer_surface, self.timer_surface_rect)
            
            pygame.display.update()
            
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
