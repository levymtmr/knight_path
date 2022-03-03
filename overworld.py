import pygame
from game_data import world_levels
from utils import import_folder 


class Node(pygame.sprite.Sprite):
    def __init__(self, pos, status, icon_speed, path):
        super().__init__()
        self.frames = import_folder(path)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.status = status
        if self.status == 'available':
            self.status = 'available'
        else:
            self.status = 'locked'
        self.rect = self.image.get_rect(center = pos)

        self.detection_zone = pygame.Rect(self.rect.centerx - (icon_speed / 2), self.rect.centery - (icon_speed / 2), icon_speed, icon_speed)

    def animate(self):
        self.frame_index += 0.15
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self):
        if self.status == 'available':
            self.animate()
        else:
            tint_surface = self.image.copy()
            tint_surface.fill('black', None, pygame.BLEND_RGBA_MULT)
            self.image.blit(tint_surface, (0,0))

class PlayerIcon(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.image = pygame.image.load('./graphics/character/hat.png')
        self.rect = self.image.get_rect(center = pos)

    def update(self):
        self.rect.center = self.pos


class Overworld:
    def __init__(self, start_level, max_level, surface, create_level):
        self.display_surface = surface
        self.max_level = max_level
        self.current_level = start_level
        self.create_level = create_level

        # movement logic
        self.moving = False
        self.move_direction = pygame.math.Vector2(0, 0)
        self.speed = 8

        self.setup_nodes()
        self.setup_player_icon()

    def setup_nodes(self):
        self.nodes = pygame.sprite.Group()

        for index, level in enumerate(world_levels):
            if index <= self.max_level:
                node_sprite = Node(world_levels.get(level).get('node_pos'), 'available', self.speed, world_levels.get(level).get('node_graphic'))
            else:
                node_sprite = Node(world_levels.get(level).get('node_pos'), 'locked', self.speed, world_levels.get(level).get('node_graphic'))
            
            self.nodes.add(node_sprite)

    def setup_player_icon(self):
        self.player_icon = pygame.sprite.GroupSingle()
        posistion = self.current_level['node_pos']
        icon_sprite = PlayerIcon(posistion)

        # icon_sprite = PlayerIcon(self.nodes.sprites()[self.current_level].rect.center)
        self.player_icon.add(icon_sprite)

    def draw_lines(self):
        '''
        append lines between the levels when the max_level change.
        if the player is allowed to the next level then the lines will be appears.
        '''
        allowed_nodes = []
        for node in self.nodes:
            if node.status == 'available':
                allowed_nodes.append((node.rect.centerx, node.rect.centery))
        pygame.draw.lines(self.display_surface, '#a04f45', False, allowed_nodes, 6)

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.moving:
            if keys[pygame.K_RIGHT] and self.current_level['stage'] < self.max_level:
                self.move_direction = self.get_movement_data('next')
                self.current_level['stage'] += 1
                self.moving = True
            elif keys[pygame.K_LEFT] and self.current_level['stage'] > 0:
                self.move_direction = self.get_movement_data('previous')
                self.current_level['stage'] -= 1
                self.moving = True
            elif keys[pygame.K_SPACE]:
                current_stage = self.current_level['stage']
                self.current_level = world_levels[str(current_stage)]
                self.create_level(self.current_level)

    def update_icon_position(self):
        if self.moving and self.move_direction:
            if self.current_level['stage'] == 0:
                self.player_icon.sprite.pos += self.move_direction * self.speed
            else:
                self.player_icon.sprite.pos += self.move_direction * self.speed
            target_node = self.nodes.sprites()[self.current_level['stage']]
            if target_node.detection_zone.collidepoint(self.player_icon.sprite.pos):
                self.moving = False
                self.move_direction = pygame.math.Vector2(0, 0)

    def get_movement_data(self, target):
        if target == 'next':
            next_stage = self.current_level['stage'] + 1
            start = pygame.math.Vector2(world_levels[str(self.current_level['stage'])]['node_pos'])
            end = pygame.math.Vector2(world_levels[str(next_stage)]['node_pos'])

        if target == 'previous':
            if self.current_level['stage'] == 0:
                return world_levels[str(self.current_level['stage'])]['node_pos']
            else:
                next_stage = self.current_level['stage'] - 1
                start = pygame.math.Vector2(world_levels[str(self.current_level['stage'])]['node_pos'])
                end = pygame.math.Vector2(world_levels[str(next_stage)]['node_pos'])
        return (end - start).normalize()

    def run(self):
        self.input()
        self.update_icon_position()
        self.player_icon.update()
        self.nodes.update()

        self.draw_lines()
        self.nodes.draw(self.display_surface)
        self.player_icon.draw(self.display_surface)
