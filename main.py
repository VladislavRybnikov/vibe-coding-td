import pygame
from game import Game

def main():
    pygame.init()
    game = Game()
    
    while game.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
            elif game.state == "menu":
                game.handle_menu_events(event)
            elif game.state == "game":
                game.handle_game_events(event)
        
        game.update()
        game.draw()
        game.clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()