import pygame
import random


class Circle:
    def __init__(self, screen):
        self.screen = screen
        self.color = (255, 255, 255)
        self.radius = 50
        self.x = screen.get_width() // 2
        self.y = screen.get_height() // 2
        self.last_draw_time = 0
        self.draw_interval = 10000  # 10 seconds in milliseconds

    def spawn(self):
        self.x = self.screen.get_width() // 2
        self.y = self.screen.get_height() // 2
        self.last_draw_time = pygame.time.get_ticks()

    def draw(self):
        now = pygame.time.get_ticks()
        time_since_last_draw = now - self.last_draw_time
        if time_since_last_draw >= self.draw_interval:
            self.spawn()
        pygame.draw.circle(self.screen, self.color,
                           (self.x, self.y), self.radius)



pygame.init()

# Set up the display
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Create a circle object
circle = Circle(screen)

# Start the game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))  # Clear the screen
    circle.draw()  # Draw the circle
    pygame.display.update()  # Update the screen

pygame.quit()
