import pygame, sys

from settings import level_map, screen_height, screen_width
from game_data import level_0
from level import Level
from overworld import Overworld

class Game:
    def __init__(self):
        self.max_level = 4
        self.overworld = Overworld(1, self.max_level, screen)

    def run(self):
        self.overworld.run()

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
game = Game()
# level = Level(level_map, screen)
level = Level(level_0, screen)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill("gray")
    game.run()

    # level.run()

    pygame.display.update()
    clock.tick(60)