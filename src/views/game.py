import arcade
import arcade.color
import math
import json
import arcade.color
from views.pause import PauseView, MoveSelectView
from sprites.player import Player
from sprites.sound_player import AmbientPlayer
from sprites.slime import Slime
from utils.camera import HKUCamera
from data import controls
from pyglet.math import Vec2
from utils.level import Level
from utils.sound import load_sound, play_sound
from utils.physics_engine import HKUEngine
from data.constants import MAP_WIDTH, MAP_HEIGHT, DELTA_TIME, BAR_SPACING, SOUND_EFFECT_VOL, MUSIC_VOL, LINE_HEIGHT, UI_FONT, UI_FONT_PATH, UI_FONT_SIZE, TILE_SIZE, M
import data.color as color

class GameSection(arcade.Section):
    def __init__(self, left: int, bottom: int, width: int, height: int,
                 **kwargs):
        super().__init__(left, bottom, width, height,
                          **kwargs)
        self.current_level_id = 0
        self.scene = None
        self.player = None
        self.tile_map = None
        self.physics_engine = None
        self.camera = None
        self.mouse_pos = (0,0)
        self.timer = 0
        self.player_by_bench = False
        self.animated_pos = []

    def setup(self):
        self.load_map("resources/maps/map2.json")
        self.player = Player(id=1, scene=self.scene)
        self.scene.add_sprite_list(name="Player", use_spatial_hash=True)
        self.scene.add_sprite("Player", self.player)
        self.scene.add_sprite_list(name="Kitty")
        self.scene.add_sprite_list(name="Enemy")
        self.scene.add_sprite_list(name="Treat")
        self.scene.add_sprite_list(name="Projectile")
        self.scene.add_sprite_list(name="Trap")
        self.scene.add_sprite_list(name="River Sounds")
        self.scene.add_sprite_list(name="Workbench")
        self.current_level_id = 0
        spawn = self.tile_map.object_lists["player spawn"][0]
        self.player.left = spawn.shape[0]
        self.player.bottom = spawn.shape[1]
        self.load_level()
        self.level_list = self.current_level.get_level_list()
        colliding_sprites = [self.scene.get_sprite_list("Player"), self.scene.get_sprite_list("Enemy"), self.scene.get_sprite_list("Kitty")]
        self.physics_engine = HKUEngine(
            colliding_sprites=colliding_sprites,
            walls=[
                self.scene["Wall"]
            ]
        )
        self.river_sound = load_sound("river1", source="hku")
        for point in self.tile_map.object_lists["river noise"]:
            x = point.shape[0]
            y = point.shape[1]
            ambient_player = AmbientPlayer(scene=self.scene, sound=self.river_sound, center_x=x, center_y=y, filename="resources/spritesheets/cat.png")
            self.scene.add_sprite("River Sounds", ambient_player)
            ambient_player.play()
        slime = Slime(scene=self.scene, filename="resources/spritesheets/slime.png", center_x= 1260, center_y=1024, scale=3, finite=True)
        self.scene.add_sprite("Trap", slime)
        map_bounds = self.tile_map.object_lists["map bounds"]
        for point in self.tile_map.object_lists["workbench"]:
            x = point.shape[0]
            y = point.shape[1] + 90
            bench = arcade.Sprite(center_x=x, center_y=y, filename="resources/spritesheets/bench.png", scale=3)
            self.scene.add_sprite("Workbench", bench)
        self.create_tile_terrain_mapping()
        self.camera = HKUCamera(self.width, self.height)
        self.player.setup()

    def on_update(self):
        self.timer += DELTA_TIME
        self.physics_engine.update()
        self.scene.update()
        self.scene.update_animation(DELTA_TIME, names=["Floor"])
        self.current_level.update_respawn_enemies()
        self.monitor_player_workbench()
        self.monitor_player_inside()

    def on_draw(self):
        self.update_camera()
        self.scene.draw(names=["Floor", "Wall", "Trap", "Treat", "Workbench", "Kitty", "Enemy", "Player", "Projectile"])
        self.draw_border()
        self.draw_button_hints()
        active_moves_player = self.player.get_active_moves()
        for move in active_moves_player:
            move.draw()
        if self.current_level.boss_fight:
            active_moves_boss = self.scene.get_sprite_list("Enemy")[0].get_active_moves()
            for move in active_moves_boss:
                move.draw()
        charging_moves = self.player.get_charge_moves()
        for move in charging_moves:
            move.draw()

    def on_key_press(self, key, modifiers):
        if key == controls.UP:
            self.player.up_pressed = True
        elif key == controls.DOWN:
            self.player.down_pressed = True
        elif key == controls.LEFT:
            self.player.left_pressed = True
        elif key == controls.RIGHT:
            self.player.right_pressed = True
        elif key == controls.INTERACT and self.player_by_bench:
            move_select_view = MoveSelectView(self.view)
            self.window.show_view(move_select_view)
        elif key == controls.SPRINT:
            self.player.sprint_pressed = True
        elif key == controls.ATTACK:
            if self.player.choosing_target:
                self.player.change_target("any")
            elif self.player.alt_pressed and self.player.equipped_moves.get("alt quick attack"):
                self.player.do_move(self.player.equipped_moves["alt quick attack"])
            elif not self.player.alt_pressed and self.player.equipped_moves.get("quick attack"):
                self.player.do_move(self.player.equipped_moves["quick attack"])
        elif key == controls.HEAL:
            if self.player.alt_pressed and self.player.equipped_moves.get("alt heal"):
                self.player.do_move(self.player.equipped_moves["alt heal"])
            elif not self.player.alt_pressed and self.player.equipped_moves.get("heal"):
                self.player.do_move(self.player.equipped_moves["heal"])
        elif key == controls.SPECIAL:
            if self.player.alt_pressed and self.player.equipped_moves.get("alt special"):
                self.player.do_move(self.player.equipped_moves["alt special"])
            elif not self.player.alt_pressed and self.player.equipped_moves.get("special"):
                self.player.do_move(self.player.equipped_moves["special"])
        elif key == controls.DROP_TREAT:
            if self.player.has_treats:
                self.player.drop_treat()
            else:
                play_sound(self.player.no_treat_sound, volume=SOUND_EFFECT_VOL*(arcade.get_window().sfx_vol))
        elif key == controls.PICKUP_TREAT:
            self.player.picking_up_treat = True
        elif key == controls.SCARE:
            if self.player.alt_pressed and self.player.equipped_moves.get("alt scare"):
                self.player.do_move(self.player.equipped_moves["alt scare"])
            elif not self.player.alt_pressed and self.player.equipped_moves.get("scare"):
                self.player.do_move(self.player.equipped_moves["scare"])
        elif key == controls.ALT_MODIFIER:
            self.player.alt_pressed = True
        elif key == controls.TARGET_UP:
            self.player.change_target("up")
        elif key == controls.TARGET_DOWN:
            self.player.change_target("down")
        elif key == controls.TARGET_LEFT:
            self.player.change_target("left")
        elif key == controls.TARGET_RIGHT:
            self.player.change_target("right")
        elif key == controls.PAUSE:
            pause_view = PauseView(self.view)
            self.window.show_view(pause_view)

    def on_key_release(self, key, modifiers):
        if key == controls.UP:
            self.player.up_pressed = False
        elif key == controls.DOWN:
            self.player.down_pressed = False
        elif key == controls.LEFT:
            self.player.left_pressed = False
        elif key == controls.RIGHT:
            self.player.right_pressed = False
        elif key == controls.SPRINT:
            self.player.sprint_pressed = False
        elif key == controls.ATTACK:
            if self.player.equipped_moves.get("quick attack"):
                self.player.stop_move(self.player.equipped_moves["quick attack"])
            if self.player.equipped_moves.get("alt quick attack"):
                self.player.stop_move(self.player.equipped_moves["alt quick attack"])
        elif key == controls.HEAL:
            if self.player.equipped_moves.get("heal"):
                self.player.stop_move(self.player.equipped_moves["heal"])
            if self.player.equipped_moves.get("alt heal"):
                self.player.stop_move(self.player.equipped_moves["alt heal"])
        elif key == controls.SPECIAL:
            if self.player.equipped_moves.get("special"):
                self.player.stop_move(self.player.equipped_moves["special"])
            if self.player.equipped_moves.get("alt special"):
                self.player.stop_move(self.player.equipped_moves["alt special"])
        elif key == controls.PICKUP_TREAT:
            self.player.picking_up_treat = False
        elif key == controls.SCARE:
            if self.player.equipped_moves.get("scare"):
                self.player.stop_move(self.player.equipped_moves["scare"])
            if self.player.equipped_moves.get("alt scare"):
                self.player.stop_move(self.player.equipped_moves["alt scare"])
        elif key == controls.ALT_MODIFIER:
            self.player.alt_pressed = False

    def monitor_player_workbench(self):
        tuple = arcade.get_closest_sprite(self.player, self.scene.get_sprite_list("Workbench"))
        bench = tuple[0]
        distance = tuple[1]
        if bench is not None:
            if distance <= 256 and (self.player.bottom<=bench.top):
                self.player_by_bench = True
            else:
                self.player_by_bench = False

    def monitor_player_inside(self):
        left = self.tile_map.object_lists["inside"][0].shape[0]
        top = self.tile_map.object_lists["inside"][0].shape[1]
        right = self.tile_map.object_lists["inside"][1].shape[0]
        bottom = self.tile_map.object_lists["inside"][1].shape[1]
        if (left <= self.player.center_x <= right) and (bottom <= self.player.center_y <= top):
            self.player.inside = True
        else:
            self.player.inside = False

    def create_tile_terrain_mapping(self):
        terrain_dict = {}
        tile_data = self.tile_map.tiled_map.tilesets[1].tiles
        for integer, tile in tile_data.items():
            if tile.properties:
                terrain_dict[tile.id] = tile.properties.get("Terrain", "unknown")
        with open('resources/maps/terrain_mapping.json', 'w') as json_file:
            json.dump(terrain_dict, json_file, indent=4)

    def update_camera(self):
        if self.player.is_alive:
            player_position_for_cam = Vec2(self.player.center_x-(self.width//2), self.player.center_y-(self.height//2))
            self.camera.move_to(player_position_for_cam)
        else:
            arcade.set_viewport(0, self.view.window.width, 0, self.view.window.height)
        self.camera.use()

    def load_map(self, map_path):
        layer_options = {
            "Wall": {
                "use_spatial_hash": True
            }
        }
        scaling = M / TILE_SIZE
        self.tile_map = arcade.load_tilemap(map_path, layer_options=layer_options, scaling=scaling, offset=(-1024, -1024))

        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        self.create_animated_tiles()

    def create_animated_tiles(self):
        animated_tiles = {}

        tileset = self.tile_map.tiled_map.tilesets[1]
        tile_data = tileset.tiles
        tileset_image = tileset.image
        tile_width = tileset.tile_width
        tile_height = tileset.tile_height
        image_width = tileset.image_width
        columns = image_width // tile_width

        for tile_id, tile in tile_data.items():
            if tile.animation:
                frames = []
                for frame in tile.animation:
                    frame_tile_id = frame.tile_id
                    row = frame_tile_id // columns
                    col = frame_tile_id % columns
                    x = col * tile_width
                    y = row * tile_height
                    texture = arcade.load_texture(tileset_image, x, y, tile_width, tile_height)
                    keyframe = arcade.AnimationKeyframe(tile_id=frame_tile_id, duration=frame.duration, texture=texture)
                    frames.append(keyframe)
                animated_tiles[tile_id] = frames

        for sprite_list in self.scene.sprite_lists:
            for sprite in sprite_list:
                tile_id = sprite.properties.get('tile_id')
                if tile_id in animated_tiles:
                    animated_sprite = arcade.AnimatedTimeBasedSprite(scale=M/TILE_SIZE)
                    animated_sprite.frames = animated_tiles[tile_id]
                    animated_sprite.texture = animated_sprite.frames[0].texture

                    animated_sprite.position = sprite.position
                    self.animated_pos.append(animated_sprite.position)

                    sprite.kill()
                    for name, list in self.scene.name_mapping.items():
                        if list == sprite_list:
                            self.scene.add_sprite(name, animated_sprite)

    def load_level(self):
        self.current_level = Level(level_id=self.current_level_id, scene=self.scene)
        self.current_level.load_enemies()
        self.current_level.load_kitties()
        self.current_level.load_traps()
        for kitty in self.scene.get_sprite_list("Kitty"):
            kitty.setup()
        for enemy in self.scene.get_sprite_list("Enemy"):
            enemy.setup()
        self.current_level.spawn_treats()

    def draw_border(self):
        border_trigger = 256
        border_width=10+math.sin(self.timer*5)*5
        nlayers = 10
        if self.player.center_x < border_trigger:
            for i in range(nlayers):
                ratio = ((256-self.player.center_x)/256)
                border_color = color.PINK[:3] + [int(0.1*(1+math.sin(self.timer*5))*255)+64*ratio]
                length = 32+96*ratio
                arcade.draw_line(0, min(MAP_HEIGHT, self.player.center_y+length*(1+i)/nlayers), 0, max(0, self.player.center_y-length*(1+i)/nlayers), color=border_color, line_width=border_width*ratio)
        if self.player.center_y < border_trigger:
            for i in range(nlayers):
                ratio = ((256-self.player.center_y)/256)
                border_color = color.PINK[:3] + [int(0.1*(1+math.sin(self.timer*5))*255)+64*ratio]
                length = 32+96*ratio
                arcade.draw_line(min(MAP_WIDTH, self.player.center_x+length*(1+i)/nlayers), 0, max(0, self.player.center_x-length*(1+i)/nlayers), 0, color=border_color, line_width=border_width*ratio)
        if self.player.center_x > MAP_WIDTH-border_trigger:
            for i in range(nlayers):
                ratio = ((256-(MAP_WIDTH-self.player.center_x))/256)
                border_color = color.PINK[:3] + [int(0.1*(1+math.sin(self.timer*5))*255)+64*ratio]
                length = 32+96*ratio
                arcade.draw_line(MAP_WIDTH, min(MAP_HEIGHT, self.player.center_y+length*(1+i)/nlayers), MAP_WIDTH, max(0, self.player.center_y-length*(1+i)/nlayers), color=border_color, line_width=border_width*ratio)
        if self.player.center_y > MAP_HEIGHT-border_trigger:
            for i in range(nlayers):
                ratio = ((256-(MAP_HEIGHT-self.player.center_y))/256)
                border_color = color.PINK[:3] + [int(0.1*(1+math.sin(self.timer*5))*255)+64*ratio]
                length = 32+96*ratio
                arcade.draw_line(min(MAP_WIDTH, self.player.center_x+length*(1+i)/nlayers), MAP_HEIGHT, max(0, self.player.center_x-length*(1+i)/nlayers), MAP_HEIGHT, color=border_color, line_width=border_width*ratio)

    def draw_button_hints(self):
        if self.player_by_bench:
            e_text = arcade.Text("E", anchor_x="center", anchor_y="center", start_x=self.player.center_x, start_y=self.player.top+32, font_size=24, width=256, font_name=UI_FONT, color=arcade.color.WHITE)
            arcade.draw_circle_filled(center_x=e_text.x, center_y=e_text.y, radius=e_text.content_width, color=arcade.color.BLACK[:3]+(128,))
            e_text.draw()

    @property
    def more_levels(self):
        return len(self.level_list) > self.current_level_id + 1

    @property
    def any_enemies(self):
        return len(self.scene.get_sprite_list("Enemy")) > 0

    @property
    def any_kitties(self):
        kitties = self.scene.get_sprite_list("Kitty")
        for kitty in kitties:
            if not (kitty.fading or kitty.faded):
                return True
        return False

    def draw_debug(self):
        self.camera.use()
        self.player.draw_debug()
        for treat in self.scene.get_sprite_list("Treat"):
            treat.draw_debug()
        for projectile in self.scene.get_sprite_list("Projectile"):
            projectile.draw_debug()


class UISection(arcade.Section):
    def __init__(self, left: int, bottom: int, width: int, height: int, **kwargs):
        super().__init__(left, bottom, width, height,
                          **kwargs)
        self.scene = None
        self.player = None
        self.kitties = None
        self.enemies = None
        self.sprite_lists = None
        self.camera = None

    def setup(self):
        self.update_sprite_lists()
        self.camera = arcade.Camera(self.width, self.height)
        arcade.load_font(UI_FONT_PATH)

    def on_update(self):
        self.update_sprite_lists()

    def on_draw(self):
        self.camera.use()
        if not (self.player.faded or self.player.fading):
            self.draw_xp_bar()
            self.draw_stamina_bar()
            self.draw_hp_bar()
            self.draw_treat_count()
            self.draw_move_status()
            if self.view.game_section.current_level.boss_fight:
                self.draw_boss_hp()
            if not self.view.completed:
                self.draw_level_id()

    def update_sprite_lists(self):
        self.scene = self.view.game_section.scene
        self.players = self.scene.get_sprite_list("Player")
        if len(self.players) > 0:
            self.player = self.players[0]
        self.kitties = self.scene.get_sprite_list("Kitty")
        self.enemies = self.scene.get_sprite_list("Enemy")
        self.sprite_lists = [self.players, self.kitties, self.enemies]

    def draw_level_id(self):
        level_text = arcade.Text(f"Level: {self.view.game_section.current_level_id}", start_x=self.right-10, start_y=self.top-100, color=arcade.color.BLACK[:3] + (128,), anchor_x="right", font_size=UI_FONT_SIZE, font_name=UI_FONT)
        level_text.draw()

    def draw_treat_count(self):
        treat_count = self.player.treat_amount
        treat_count_text = arcade.Text(f"Treats: {treat_count}", start_x=self.right-10, start_y=self.top-140, color=arcade.color.BLACK[:3] + (128,), anchor_x="right", font_size=UI_FONT_SIZE, font_name=UI_FONT)
        treat_count_text.draw()

    def draw_stamina_bar(self):
        if self.player:
            filled_width = (self.player.stamina / self.player.max_stamina) * 100
            arcade.draw_rectangle_filled(center_x=self.left + 100,
                                         center_y=self.bottom + 70,
                                         width=100,
                                         height=10,
                                         color=arcade.color.BLACK[:3] + (128,))
            arcade.draw_rectangle_filled(center_x=self.left + 100 - (50 - filled_width / 2),
                                         center_y=self.bottom + 70,
                                         width=filled_width,
                                         height=10,
                                         color=arcade.color.GREEN[:3] + (200,))

    def draw_hp_bar(self):
        if self.player:

            filled_width = (self.player.hp / self.player.max_hp) * 100

            arcade.draw_rectangle_filled(center_x=self.left + 100,
                                         center_y=self.bottom + 120,
                                         width=100,
                                         height=10,
                                         color=arcade.color.BLACK[:3] + (128,))

            arcade.draw_rectangle_filled(center_x=self.left + 100 - (50 - filled_width / 2),
                                         center_y=self.bottom + 120,
                                         width=filled_width,
                                         height=10,
                                         color=arcade.color.RED[:3] + (200,))

    def draw_boss_hp(self):
        boss = self.enemies[0]
        base_width = 600
        height = 80
        filled_width = (boss.hp / boss.max_hp) * base_width

        arcade.draw_rectangle_filled(center_x=self.width // 2,
                                     center_y=self.bottom + 120,
                                     width=base_width,
                                     height=height,
                                     color=arcade.color.BLACK[:3] + (128,))

        arcade.draw_rectangle_filled(center_x=self.width // 2 - (base_width/2 - filled_width / 2),
                                     center_y=self.bottom + 120,
                                     width=filled_width,
                                     height=height,
                                     color=arcade.color.RED[:3] + (200,))


    def draw_move_status(self):
        bar_height = 10
        y_offset = 96
        slot_index = {
            "quick attack": 1,
            "alt quick attack": 1,
            "special": 2,
            "alt special": 2,
            "heal": 3,
            "alt heal": 3,
            "scare": 4,
            "alt scare": 4,
            "drop treat": 5,
            "alt drop treat": 5,
            "pickup treat": 6,
            "alt pickup treat": 6,
        }
        for slot, move in self.player.equipped_moves.items():
            if move is not None:
                self._draw_rectangle_filled(slot_index[slot], slot, move.progress_fraction, move.color, y_offset, (100, bar_height))
                self._draw_rectangle_filled(slot_index[slot], slot, move.refresh_fraction, move.color, y_offset+bar_height, (100, bar_height))
                self._draw_rectangle_filled(slot_index[slot], slot, move.charge_fraction, move.color, y_offset+2*bar_height, (100, bar_height))

    def _draw_rectangle_filled(self, slot_index, slot, progress_fraction, color, center_y_offset, size):
        filled_width = progress_fraction * size[0]
        alt = int(slot[0:4] == "alt ")
        arcade.draw_rectangle_filled(center_x=self.left + 100 + (size[0]+10)*alt,
                                    center_y=self.bottom + center_y_offset + (slot_index * BAR_SPACING),
                                    width=size[0],
                                    height=size[1],
                                    color=arcade.color.BLACK[:3]+(128,))

        arcade.draw_rectangle_filled(center_x=self.left + 100 + (size[0]+10)*alt - (size[0] / 2 - filled_width / 2),
                                    center_y=self.bottom + center_y_offset + (slot_index * BAR_SPACING),
                                    width=filled_width,
                                    height=size[1],
                                    color=color)


    def draw_xp_bar(self):
        if self.player.at_max_rank:
            max_rank_text = arcade.Text(f"MAX RANK", start_x=self.width // 2, start_y=self.top - 70, color=arcade.color.BLACK[:3] + (128,), anchor_x="center", anchor_y="center", font_size=UI_FONT_SIZE*1.5, font_name=UI_FONT)
            max_rank_text.draw()
        else:
            filled_width = max(0,(self.player.get_xp_fraction()) * 300)
            arcade.draw_rectangle_filled(center_x=self.width // 2,
                                                center_y=self.top - 70,
                                                width=300,
                                                height=20,
                                                color=arcade.color.BLACK[:3] + (128,))

            arcade.draw_rectangle_filled(center_x=self.width // 2 - 150 + filled_width / 2,
                                        center_y=self.top - 70,
                                        width=filled_width,
                                        height=20,
                                        color=arcade.color.YELLOW[:3] + (128,))

            current_rank_text = arcade.Text(f"{self.player.current_rank}", start_x=self.width // 2 - 175, start_y=self.top - 70, color=arcade.color.BLACK[:3] + (128,),anchor_x="center", anchor_y="center", font_size=UI_FONT_SIZE, font_name=UI_FONT)
            next_rank_text = arcade.Text(f"{self.player.current_rank+1}", start_x=self.width // 2 + 175, start_y=self.top - 70, color=arcade.color.BLACK[:3] + (128,), anchor_x="center", anchor_y="center", font_size=UI_FONT_SIZE, font_name=UI_FONT)
            current_rank_text.draw()
            next_rank_text.draw()

    def get_player(self):
        return self.view.game_section.player

class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.window.views["game"] = self
        self.main_menu = None
        self.game_section = GameSection(0, 0,
                                       self.window.width, self.window.height, accept_keyboard_events=True)
        self.ui_section = UISection(0, 0,
                                   self.window.width, self.window.height)

        self.sectionManager = arcade.SectionManager(self)
        self.sectionManager.add_section(self.game_section)
        self.sectionManager.add_section(self.ui_section)

        self.between_levels = True
        self.between_levels_timer = 0
        self.between_levels_time = 5

        self.debug = False
        self.loaded_sound = load_sound("upgrade1")

        self.media_player = None
        self.songs = {
            "normal": "resources/sounds/music/hkusong1.wav",
            "battle": "resources/sounds/music/battlemusic1.wav"
        }

        self.curr_song_key = "normal"

        self.my_music = arcade.load_sound(self.songs[self.curr_song_key])

        self.crossfade_time = 1
        self.crossfade_timer = 0
        self.new_media_player = None

        self.out_of_battle_timer = 0
        self.time_out_of_battle = 2

        self.mouse_pos = (0,0)

    def setup(self):
        self.game_section.setup()
        self.ui_section.setup()

    def on_show_view(self):
        self.window.set_mouse_visible(False)
        play_sound(self.loaded_sound, volume=SOUND_EFFECT_VOL*(arcade.get_window().sfx_vol))
        arcade.set_background_color(arcade.color.BLUE_SAPPHIRE)
        self.play_music(self.curr_song_key)

    def on_hide_view(self):
        self.window.set_mouse_visible()
        if self.media_player:
            self.media_player.pause()
            if self.new_media_player:
                self.new_media_player.pause()

    def on_draw(self):
        self.clear()

        self.game_section.on_draw()
        self.ui_section.on_draw()

        if self.completed:
            self.draw_victory_message()
        elif self.game_section.player.is_dead:
            self.draw_defeat_message()

        if self.debug:
            self.draw_debug()

    def on_update(self, delta_time=DELTA_TIME):
        self.game_section.on_update()
        self.ui_section.on_update()
        self.handle_gamestate()
        self.update_between_levels()
        self.update_music()

    def update_music(self, delta_time=DELTA_TIME):
        self.media_player.volume = MUSIC_VOL*arcade.get_window().music_vol
        if self.game_section.player.in_battle:
            self.out_of_battle_timer = 0
            new_song_key = "battle"
        else:
            if self.curr_song_key == "battle":
                self.out_of_battle_timer += delta_time
                if self.out_of_battle_timer >= self.time_out_of_battle:
                    new_song_key = "normal"
                else:
                    new_song_key = self.curr_song_key
            else:
                new_song_key = "normal"

        if new_song_key != self.curr_song_key:
            self.curr_song_key = new_song_key
            self.crossfade_to_new_music(new_song_key)

        if self.crossfade_timer > 0:
            self.crossfade_timer -= delta_time
            progress = (self.crossfade_time - self.crossfade_timer) / self.crossfade_time
            if self.media_player:
                self.media_player.volume = max(0, 1 - progress) * MUSIC_VOL*(arcade.get_window().music_vol)
            if self.new_media_player:
                self.new_media_player.volume = min(1, progress) * MUSIC_VOL*(arcade.get_window().music_vol)

            if self.crossfade_timer <= 0:
                if self.media_player:
                    self.media_player.pause()
                self.media_player = self.new_media_player
                self.new_media_player = None

    def crossfade_to_new_music(self, song_key):
        self.crossfade_timer = self.crossfade_time
        self.new_music = arcade.load_sound(self.songs[song_key])
        self.new_media_player = self.new_music.play(volume=0)
        if self.media_player:
            self.media_player.volume = 1 * MUSIC_VOL*(arcade.get_window().music_vol)

    def play_music(self, song_key):
        if self.media_player:
            self.media_player.pause()
        self.my_music = arcade.load_sound(self.songs[song_key])
        self.media_player = self.my_music.play(loop=True, volume=MUSIC_VOL*(arcade.get_window().music_vol))

    def start_between_levels(self):
        self.between_levels = True
        self.between_levels_timer = 0
        self.game_section.player.give_xp(25*self.game_section.current_level_id)
        enemies = self.game_section.scene.get_sprite_list("Enemy")
        for enemy in enemies:
            enemy.start_fade()
        treats = self.game_section.scene.get_sprite_list("Treat")
        for treat in treats:
            treat.kill()


    def update_between_levels(self):
        if self.between_levels:
            self.between_levels_timer += DELTA_TIME
            if self.between_levels_timer > self.between_levels_time:
                self.between_levels = False
                self.handle_level_completion()
                self.between_levels_timer = 0

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        a_x = x+self.game_section.camera.position.x
        a_y = y+self.game_section.camera.position.y
        self.mouse_pos = (a_x, a_y)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.APOSTROPHE:
            self.debug = not self.debug

        self.game_section.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        self.game_section.on_key_release(key, modifiers)

    def draw_debug(self):
        self.ui_section.camera.use()

        enemy_count = len(self.game_section.scene.get_sprite_list("Enemy"))
        kitty_count = len(self.game_section.scene.get_sprite_list("Kitty"))
        kitty_count_max = self.game_section.current_level.kitty_amount
        treat_count = len(self.game_section.scene.get_sprite_list("Treat"))
        projectile_count = len(self.game_section.scene.get_sprite_list("Projectile"))
        player_pos = self.game_section.player.get_integer_position()
        terrain = self.game_section.player.walking_on
        boss_fight = self.game_section.current_level.boss_fight

        debug_text = arcade.Text(f"Debug Info\nEnemies: {enemy_count}\nKitties: {kitty_count}/{kitty_count_max}\nTreats on floor: {treat_count}\nPlayer Pos: {player_pos}\nMouse: {self.mouse_pos}\nProjectiles: {projectile_count}\nTerrain: {terrain}\nBoss fight: {boss_fight}", start_x=20, start_y=self.window.height - 20, color=arcade.color.RED, font_size=12, anchor_x="left", anchor_y="top", multiline=True, width=256)
        debug_text.draw()
        if self.between_levels:
            between_levels_text = arcade.Text(f"Between Levels {int((self.between_levels_timer/self.between_levels_time)*100)}%", start_x=20, start_y=self.window.height - 20 - LINE_HEIGHT*12, color=arcade.color.RED, font_size=12, anchor_x="left", anchor_y="top")
            between_levels_text.draw()


        self.game_section.camera.use()
        self.game_section.draw_debug()
        enemies = self.game_section.scene.get_sprite_list("Enemy")
        for enemy in enemies:
            enemy.draw_debug()
        kitties = self.game_section.scene.get_sprite_list("Kitty")
        for kitty in kitties:
            kitty.draw_debug()

    def draw_victory_message(self):
        self.game_section.camera.use()
        victory_message_text = arcade.Text(f"VICTORY", start_x=self.game_section.player.center_x, start_y=self.game_section.player.center_y+100, color=arcade.color.BLACK, font_size=24, anchor_x="center")
        victory_message_text.draw()

    def draw_defeat_message(self):
        self.ui_section.camera.use()
        death_message_text = arcade.Text(f"YOU HAVE DIED", start_x=self.ui_section.width // 2, start_y=self.ui_section.height // 2, color=arcade.color.BLACK, font_size=24, anchor_x="center")
        death_message_text.draw()

    def handle_gamestate(self):
        if self.should_change_level:
            self.start_between_levels()

    def handle_level_completion(self):
        if not self.between_levels:
            if self.game_section.more_levels:
                self.game_section.current_level_id += 1
                self.game_section.load_level()

    @property
    def should_change_level(self):
        if self.game_section.current_level.boss_fight:
            return not self.between_levels and not self.game_section.any_enemies
        else:
            return not self.between_levels and not self.game_section.any_kitties

    @property
    def completed(self):
        if self.game_section.current_level.boss_fight:
            return not self.game_section.more_levels and not self.game_section.any_enemies
        else:
            return not self.game_section.more_levels and not self.game_section.any_kitties


    def to_dict(self):
        unlocked_moves = []
        for move in self.game_section.player.unlocked_moves:
            unlocked_moves.append(move.name)
        equipped_moves = {}
        for slot, move in self.game_section.player.equipped_moves.items():
            if move is not None:
                equipped_moves[slot] = move.name
        return {
            "xp": self.game_section.player.xp,
            "level": self.game_section.current_level_id,
            "unlocked moves": unlocked_moves,
            "equipped moves": equipped_moves,
            "position": self.game_section.player.get_integer_position(),
            "settings": {
                "sfx vol": round(arcade.get_window().sfx_vol, 2),
                "music vol": round(arcade.get_window().music_vol, 2)
            }
        }

    def from_dict(self, data):
        #print("\nLOADING_SAVE\n======")
        if 'xp' in data:
            #print(f"xp:{data['xp']}")
            self.game_section.player.give_xp(data['xp'])
        if 'level' in data:
            #print(f"level:{data['level']}")
            if data['level'] == 0:
                self.game_section.current_level_id = data['level']
            else:
                self.game_section.current_level_id = data['level'] - 1
            self.between_levels = True
        #print("======")
        if 'unlocked moves' in data:
            for move_name in data['unlocked moves']:
                for move in self.game_section.player.all_moves:
                    if move.name == move_name:
                        #print(f"{move.name.upper()} UNLOCKED")
                        self.game_section.player.unlock_moves(move)
        #print("======")
        if 'equipped moves' in data:
            for slot, move_name in data['equipped moves'].items():
                for move in self.game_section.player.unlocked_moves:
                    if move.name == move_name:
                        #print(f"{move.name.upper()} EQUIPPED")
                        self.game_section.player.equip_move(slot, move)
        #print("======")
        if 'position' in data:
            #print(f"xy:{data['position']}")
            self.game_section.player.position = data['position']
        #print("======")
        if 'settings' in data:
            #print(f"sfx vol: {data['settings']['sfx vol']}\nmusic vol: {data['settings']['music vol']}")
            arcade.get_window().sfx_vol = data['settings']['sfx vol']
            arcade.get_window().music_vol = data['settings']['music vol']
        #print("======")
