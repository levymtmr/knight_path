from overworld import Overworld
from level import Level
from game_data import world_levels

class Game:
    def __init__(self, screen):
        self.max_level = 2
        self.screen = screen

        # self.create_level calling the method in other instance, overworld class
        self.overworld = Overworld(world_levels['0'], self.max_level, screen, self.create_level)
        self.status = 'overworld'

    def create_level(self, current_level):
        '''
        This method is called inside the overworld class.
        '''
        self.level = Level(current_level, self.screen, self.create_overworld)
        self.status = 'level'

    def create_overworld(self, current_level, new_max_level):
        if new_max_level >= self.max_level:
            self.max_level = new_max_level
        self.overworld = Overworld(current_level, self.max_level, self.screen, self.create_level)
        self.status = 'overworld'

    def run(self):
        if self.status == 'overworld':
            self.overworld.run()
        else:
            self.level.run()

