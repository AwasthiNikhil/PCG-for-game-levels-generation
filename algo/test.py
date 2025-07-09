import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Ball properties
BALL_RADIUS = 20
ball_x = SCREEN_WIDTH // 2
ball_y = SCREEN_HEIGHT // 2
ball_speed_x = 5
ball_speed_y = 0
gravity = 0.5
jump_strength = -10
on_ground = False

# Platform properties
platforms = [
    pygame.Rect(200, 500, 400, 20),
    pygame.Rect(100, 400, 200, 20),
    pygame.Rect(500, 300, 200, 20),
]

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ball with Gravity and Jump")

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Get keys pressed
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        ball_x -= ball_speed_x
    if keys[pygame.K_RIGHT]:
        ball_x += ball_speed_x
    if keys[pygame.K_SPACE] and on_ground:
        ball_speed_y = jump_strength
        on_ground = False

    # Apply gravity
    ball_speed_y += gravity
    ball_y += ball_speed_y

    # Check for collisions with platforms
    ball_rect = pygame.Rect(ball_x - BALL_RADIUS, ball_y - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
    on_ground = False
    for platform in platforms:
        if ball_rect.colliderect(platform) and ball_speed_y > 0:
            ball_y = platform.top - BALL_RADIUS
            ball_speed_y = 0
            on_ground = True

    # Prevent the ball from falling below the screen
    if ball_y > SCREEN_HEIGHT - BALL_RADIUS:
        ball_y = SCREEN_HEIGHT - BALL_RADIUS
        ball_speed_y = 0
        on_ground = True

    # Fill the screen with white
    screen.fill(WHITE)

    # Draw the platforms
    for platform in platforms:
        pygame.draw.rect(screen, BLUE, platform)

    # Draw the ball
    pygame.draw.circle(screen, RED, (ball_x, ball_y), BALL_RADIUS)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)