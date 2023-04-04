import pygame
import menu

pygame.init()
pygame.font.init()


#header icon
pygame.display.set_icon(pygame.image.load('assets/bg.jpg'))

# main game
if __name__ == '__main__':
    # Set up the screen
    screen = pygame.display.set_mode((800, 600))

    # Show the loading screen
    loading_screen = menu.LoadingScreen(screen)
    loading_screen.run()

    # Show the start menu
    start_menu = menu.StartMenu(screen)
    start_menu.run()
