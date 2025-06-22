from settings import *
from gamestatemanager import GameStateManager

# Initialize Pygame
pygame.init()

# Main function
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Game State Manager")
    manager = GameStateManager(screen)
    manager.run()

if __name__ == "__main__":
    main()
