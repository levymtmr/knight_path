import pygame

from tiles import Coin, Crate, Tile, StaticTile, Palm, Grass
from settings import tile_size, screen_width, screen_height
from player import Player
from enemy import Enemy
from particles import ParticleEffect
from utils import import_csv_layout, import_cut_graphics
from decoration import Cloud, Sky, Water
from game_data import world_levels

class Level:
    def __init__(self, current_level, surface, create_overworld):
        # group of tiles
        self.tiles = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()

        self.current_level = current_level
        self.level_content = self.current_level['content']
        self.new_max_level = self.current_level['unlock']
        self.level_data = self.current_level['data']

        # level setup
        self.display_surface = surface
        self.setup_level(self.level_data)
        self.world_shift = 0
        self.current_x = 0
        self.create_overworld = create_overworld

        # dust
        self.dust_sprite = pygame.sprite.GroupSingle()

        self.player_on_ground = False

        # import layouts
        terrain_layout = import_csv_layout(self.level_data['terrain'])
        self.terrain_sprites = self.create_tile_group(terrain_layout, 'terrain')

        grass_layout = import_csv_layout(self.level_data['grass'])
        self.grass_sprites = self.create_tile_group(grass_layout, 'grass')

        crates_layout = import_csv_layout(self.level_data['crates'])
        self.crates_sprites = self.create_tile_group(crates_layout, 'crates')

        coins_layout = import_csv_layout(self.level_data['coins'])
        self.coins_sprites = self.create_tile_group(coins_layout, 'coins')

        fg_palms_layout = import_csv_layout(self.level_data['fg_palms'])
        self.fg_palms_sprites = self.create_tile_group(fg_palms_layout, 'fg_palms')

        bg_palms_layout = import_csv_layout(self.level_data['bg_palms'])
        self.bg_palms_sprites = self.create_tile_group(bg_palms_layout, 'bg_palms')

        # enemy
        enemy_layout = import_csv_layout(self.level_data['enemies'])
        self.enemy_sprites = self.create_tile_group(enemy_layout, 'enemies')

        # constraints
        constraints_layout = import_csv_layout(self.level_data['constraints'])
        self.constraints_sprites = self.create_tile_group(constraints_layout, 'constraint')

        # decoration
        self.sky = Sky(8)
        level_width = len(terrain_layout[0]) * tile_size
        self.water = Water(screen_height - 20, level_width)
        self.clouds = Cloud(400, level_width, 30)

        # text logs
        self.font = pygame.font.Font(None, 12)
        self.text_surface = self.font.render(self.level_content, True, 'white')
        self.text_rect = self.text_surface.get_rect(center = (screen_width / 2, screen_height / 2))

    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, value in enumerate(row):
                if value != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == 'terrain':
                        terrain_tile_list = import_cut_graphics('./graphics/terrain/terrain_tiles.png')
                        tile_surface = terrain_tile_list[int(value)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'grass':
                        grass_tile_list = import_cut_graphics('./graphics/decoration/grass/grass.png')
                        tile_surface = grass_tile_list[int(value)]
                        sprite = Grass(tile_size, x, y, tile_surface)
                    
                    if type == 'crates':
                        sprite = Crate(tile_size, x, y)

                    if type == 'coins':
                        if value == '0': sprite = Coin(tile_size, x, y, './graphics/coins/gold')
                        if value == '1': sprite = Coin(tile_size, x, y, './graphics/coins/silver')

                    if type == 'fg_palms':
                        if value == '0': sprite = Palm(tile_size, x, y, './graphics/terrain/palm_small', 38)
                        if value == '1': sprite = Palm(tile_size, x, y, './graphics/terrain/palm_large', 64)

                    if type == 'bg_palms':
                        sprite = Palm(tile_size, x, y, './graphics/terrain/palm_bg', 64)

                    if type == 'enemies':
                        sprite = Enemy(tile_size, x, y)

                    if type == 'constraint':
                        sprite = Tile((x, y), tile_size)

                    sprite_group.add(sprite)

        return sprite_group

    def create_jump_particles(self, pos):
        if self.player.sprite.facing_right:
            pos -= pygame.math.Vector2(10, 5)
        else:
            pos += pygame.math.Vector2(10, -5)

        jump_particles_sprite = ParticleEffect(pos, 'jump')
        self.dust_sprite.add(jump_particles_sprite)

    def create_landing_dust(self):
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprite:
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(10, 15)
            else:
                offset = pygame.math.Vector2(-10, 15)
            fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset, 'land')
            self.dust_sprite.add(fall_dust_particle)

    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False

    def setup_level(self, layout):
        for row_index, row in enumerate(layout):
            for col_index, cell in enumerate(row):
                # add the value position for each iteration match.
                pos_x = col_index * tile_size
                pos_y = row_index * tile_size
                if cell == 'x':
                    tile = Tile((pos_x, pos_y), tile_size)
                    self.tiles.add(tile)
                if cell == 'p':
                    self.player_sprite = Player((200, 200), self.display_surface, self.create_jump_particles)
                    self.player.add(self.player_sprite)

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        if player_x < (screen_width / 4) and direction_x < 0:
            self.world_shift = 5
            player.speed = 0
        elif player_x > screen_width - (screen_width / 4) and direction_x > 0:
            self.world_shift = -5
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 5

    def horizontal_movement_colission(self):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed

        for sprite in self.terrain_sprites:
            if sprite.rect.colliderect(player.rect) and not self.constraints_sprites:
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left 
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right

        if player.on_left and (player.rect.left < self.current_x or player.direction.x >= 0):
            player.on_left = False
        if player.on_right and (player.rect.right > self.current_x or player.direction.x <= 0):
            player.on_right = False

    def vertical_movement_colission(self):
        player = self.player.sprite
        player.apply_gravity()

        for sprite in self.terrain_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 0.1:
            player.on_ceiling = False

    def show_variable_interactions(self):
        world_shift_text = self.font.render(f" \
        World shift: {self.world_shift} \
        Gravity: {self.player_sprite.gravity} \
        Player direction: {self.player_sprite.direction} \
        Player speed: {self.player_sprite.speed} \
        Player jump: {self.player_sprite.jump_speed} \
        Player status: {self.player_sprite.status} \
        PLayer facing right: {self.player_sprite.facing_right} \
        Player on ground: {self.player_sprite.on_ground} \
        Player on ceiling: {self.player_sprite.on_ceiling}", True, (255, 255, 255), (0, 0, 0))
        self.display_surface.blit(world_shift_text, (10, 10))

    def enemy_collision_reverse(self):
        for enemy in self.enemy_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.constraints_sprites, False):
                enemy.reverse_movement()

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            current_stage = self.current_level['stage']
            self.current_level = world_levels[str(current_stage)]
            self.create_overworld(self.current_level, self.new_max_level)
        if keys[pygame.K_ESCAPE]:
            current_stage = self.current_level['stage']
            self.current_level = world_levels[str(current_stage)]
            self.create_overworld(self.current_level, 0)

    def check_death(self):
        if self.player_sprite.rect.top > screen_height:
            current_stage = self.current_level['stage']
            self.current_level = world_levels[str(current_stage)]
            self.create_overworld(self.current_level, 0)

    def check_win(self):
        '''
        Needs to create a win condition.
        '''
        if pygame.sprite.spritecollide(self.player_sprite, self.goal, False):
            current_stage = self.current_level['stage']
            self.current_level = world_levels[str(current_stage)]
            self.create_overworld(self.current_level, self.new_max_level)

    def run(self):
        self.input()
        # sky
        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface, self.world_shift)

        # dust particles
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)

        # tiles draw
        # self.tiles.update(self.world_shift)
        # self.tiles.draw(self.display_surface)
        self.scroll_x()

        # bg_palms
        self.bg_palms_sprites.update(self.world_shift)
        self.bg_palms_sprites.draw(self.display_surface)

        # player draw
        self.player.update()
        self.horizontal_movement_colission()
        self.get_player_on_ground()
        self.vertical_movement_colission()
        self.create_landing_dust()
        self.player.draw(self.display_surface)

        # enemy draw
        self.enemy_sprites.update(self.world_shift)
        self.constraints_sprites.update(self.world_shift)
        self.enemy_collision_reverse()
        self.enemy_sprites.draw(self.display_surface)

        # fg_palms
        self.fg_palms_sprites.update(self.world_shift)
        self.fg_palms_sprites.draw(self.display_surface)

        # terrain
        self.terrain_sprites.update(self.world_shift)
        self.terrain_sprites.draw(self.display_surface)

        # crates
        self.crates_sprites.update(self.world_shift)
        self.crates_sprites.draw(self.display_surface)

        # grass
        self.grass_sprites.update(self.world_shift)
        self.grass_sprites.draw(self.display_surface)

        # coins
        self.coins_sprites.update(self.world_shift)
        self.coins_sprites.draw(self.display_surface)

        # water
        self.water.draw(self.display_surface, self.world_shift)

        # show level texts
        self.display_surface.blit(self.text_surface, self.text_rect)

        # checks win and death
        self.check_death()
        self.check_win()

        # log text
        self.show_variable_interactions()
        