import arcade
import arcade.color
from src.views.pause import PauseView
from src.sprites.player import Player
from utils.camera import HKUCamera
from src.data import controls
from pyglet.math import Vec2
from src.utils.move import Move
from src.utils.move_affect_all_in_range import AffectAllMove
from src.utils.move_target_arrowkey import TargetArrowKey
from src.utils.level import Level
from src.utils.sound import play_sound
from src.data.constants import MAP_WIDTH, MAP_HEIGHT, DELTA_TIME, BAR_SPACING, CIRCLE_RADIUS, SOUND_EFFECT_VOL, LINE_HEIGHT, UI_FONT, UI_FONT_PATH, UI_FONT_SIZE

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

    def setup(self):
        self.load_map("resources/maps/map.json")
        self.player = Player(id=1, scene=self.scene)
        self.scene.add_sprite_list(name="Player", use_spatial_hash=True)
        self.scene.add_sprite("Player", self.player)
        self.scene.add_sprite_list(name = "Kitty")
        self.scene.add_sprite_list(name = "Enemy")
        self.scene.add_sprite_list(name="Treat")

        self.current_level_id = 0
        self.load_level()
        self.level_list = self.current_level.get_level_list()
        self.current_level.spawn_player()
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player,
            walls=[
                self.scene["Wall"]
            ]
        )
        self.camera = HKUCamera(self.width, self.height)
        self.player.setup()

    def on_update(self):
        self.physics_engine.update()
        self.update_camera()
        self.scene.update()

    def on_draw(self):
        self.scene.draw()
        active_moves = self.player.get_active_moves()
        for move in active_moves:
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
        elif key == controls.SPRINT:
            self.player.sprint_pressed = True
        elif key == controls.ATTACK:
            if self.player.choosing_target:
                self.player.change_target("any")
            elif modifiers == controls.ALT_MODIFIER and self.player.equipped_moves["alt quick attack"]:
                self.player.do_move(self.player.equipped_moves["alt quick attack"])
            elif self.player.equipped_moves["quick attack"]:
                self.player.do_move(self.player.equipped_moves["quick attack"])
        elif key == controls.HEAL:
            if modifiers == controls.ALT_MODIFIER and self.player.equipped_moves["alt heal"]:
                self.player.do_move(self.player.equipped_moves["alt heal"])
            elif self.player.equipped_moves["heal"]:
                self.player.do_move(self.player.equipped_moves["heal"])
        elif key == controls.SPECIAL:
            if modifiers == controls.ALT_MODIFIER and self.player.equipped_moves["alt special"]:
                self.player.do_move(self.player.equipped_moves["alt special"])
            elif self.player.equipped_moves["special"]:
                self.player.do_move(self.player.equipped_moves["special"])
        elif key == controls.DROP_TREAT:
            if self.player.has_treats:
                self.player.drop_treat()
            else:
                play_sound(self.player.no_treat_sound, volume=SOUND_EFFECT_VOL)
        elif key == controls.PICKUP_TREAT:
            self.player.picking_up_treat = True
        elif key == controls.SCARE:
            if modifiers == controls.ALT_MODIFIER and self.player.equipped_moves["alt scare"]:
                self.player.do_move(self.player.equipped_moves["alt scare"])
            elif self.player.equipped_moves["scare"]:
                self.player.do_move(self.player.equipped_moves["scare"])
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
            if modifiers == controls.ALT_MODIFIER and self.player.equipped_moves["alt quick attack"]:
                self.player.stop_move(self.player.equipped_moves["alt quick attack"])
            elif self.player.equipped_moves["quick attack"]:
                self.player.stop_move(self.player.equipped_moves["quick attack"])
        elif key == controls.HEAL:
            if modifiers == controls.ALT_MODIFIER and self.player.equipped_moves["alt heal"]:
                self.player.stop_move(self.player.equipped_moves["alt heal"])
            elif self.player.equipped_moves["heal"]:
                self.player.stop_move(self.player.equipped_moves["heal"])
        elif key == controls.SPECIAL:
            if modifiers == controls.ALT_MODIFIER and self.player.equipped_moves["alt special"]:
                self.player.stop_move(self.player.equipped_moves["alt special"])
            elif self.player.equipped_moves["special"]:
                self.player.stop_move(self.player.equipped_moves["special"])
        elif key == controls.PICKUP_TREAT:
            self.player.picking_up_treat = False
        elif key == controls.SCARE:
            if modifiers == controls.ALT_MODIFIER and self.player.equipped_moves["alt scare"]:
                self.player.stop_move(self.player.equipped_moves["alt scare"])
            elif self.player.equipped_moves["scare"]:
                self.player.stop_move(self.player.equipped_moves["scare"])

    def update_camera(self):
        if self.player.is_alive:
            player_position_for_cam = Vec2(self.player.center_x-(self.width//2), self.player.center_y-(self.height//2))
            self.camera.move_to(player_position_for_cam)
        else:
            arcade.set_viewport(0, self.view.window.width, 0, self.view.window.height)
        self.camera.use()

    def load_map(self, map_path):
        layer_options = {
            "Walls": {
                "use_spatial_hash": True
            }
        }
        self.tile_map = arcade.load_tilemap(map_path, layer_options=layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

    def load_level(self):
        self.current_level = Level(level_id=self.current_level_id, scene=self.scene)
        self.current_level.load_enemies()
        self.current_level.load_kitties()
        for kitty in self.scene.get_sprite_list("Kitty"):
            kitty.setup()
        for enemy in self.scene.get_sprite_list("Enemy"):
            enemy.setup()
        self.current_level.give_player_treats()

    @property
    def more_levels(self):
        return len(self.level_list) > self.current_level_id + 1

    @property
    def any_enemies(self):
        return len(self.scene.get_sprite_list("Enemy")) > 0

    @property
    def any_kitties(self):
        return len(self.scene.get_sprite_list("Kitty")) > 0

    def draw_debug(self):
        self.camera.use()
        self.player.draw_debug()
        for enemy in self.scene.get_sprite_list("Enemy"):
            arcade.draw_line(self.player.center_x, self.player.center_y, enemy.center_x, enemy.center_y, arcade.color.AMARANTH_PINK, 5)
        for kitty in self.scene.get_sprite_list("Kitty"):
            arcade.draw_line(self.player.center_x, self.player.center_y, kitty.center_x, kitty.center_y, arcade.color.ORANGE, 5)
        for treat in self.scene.get_sprite_list("Treat"):
            treat.draw_debug()


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
            self.draw_move_activity_bars()
            self.draw_move_charge_bars()
            self.draw_move_refresh_circles()
            if not self.view.completed:
                self.draw_level_id()

    def update_sprite_lists(self):
        self.scene = self.view.game_section.scene
        self.players = self.scene.get_sprite_list("Player")
        self.player = self.players[0]
        self.kitties = self.scene.get_sprite_list("Kitty")
        self.enemies = self.scene.get_sprite_list("Enemy")
        self.sprite_lists = [self.players, self.kitties, self.enemies]

    def draw_level_id(self):
        level_text = arcade.Text(f"Level: {self.view.game_section.current_level_id}", start_x=self.right-10, start_y=self.top-100, color=arcade.color.BLACK, anchor_x="right", font_size=UI_FONT_SIZE, font_name=UI_FONT)
        level_text.draw()

    def draw_treat_count(self):
        treat_count = self.player.treat_amount
        treat_count_text = arcade.Text(f"Treats: {treat_count}", start_x=self.right-10, start_y=self.top-140, color=arcade.color.BLACK, anchor_x="right", font_size=UI_FONT_SIZE, font_name=UI_FONT)
        treat_count_text.draw()

    def draw_stamina_bar(self):
        if self.player:
            filled_width = (self.player.stamina / self.player.max_stamina) * 100
            arcade.draw_rectangle_filled(center_x=self.left + 100,
                                         center_y=self.bottom + 70,
                                         width=100,
                                         height=10,
                                         color=arcade.color.BLACK)
            arcade.draw_rectangle_filled(center_x=self.left + 100 - (50 - filled_width / 2),
                                         center_y=self.bottom + 70,
                                         width=filled_width,
                                         height=10,
                                         color=arcade.color.GREEN)

    def draw_hp_bar(self):
        if self.player:

            filled_width = (self.player.hp / self.player.max_hp) * 100

            arcade.draw_rectangle_filled(center_x=self.left + 100,
                                         center_y=self.bottom + 120,
                                         width=100,
                                         height=10,
                                         color=arcade.color.BLACK)

            arcade.draw_rectangle_filled(center_x=self.left + 100 - (50 - filled_width / 2),
                                         center_y=self.bottom + 120,
                                         width=filled_width,
                                         height=10,
                                         color=arcade.color.RED)

    def draw_move_activity_bars(self):
        if self.player.doing_move:
            moves = self.player.get_active_moves()
            for move_index, move in enumerate(moves):
                filled_width = (move.progress_fraction) * 100
                arcade.draw_rectangle_filled(center_x=self.left + 100,
                                            center_y=self.bottom + 220 + (move_index * BAR_SPACING),
                                            width=100,
                                            height=10,
                                            color=arcade.color.BLACK)
                arcade.draw_rectangle_filled(center_x=self.left + 100 - (50 - filled_width / 2),
                                            center_y=self.bottom + 220 + (move_index * BAR_SPACING),
                                            width=filled_width,
                                            height=10,
                                            color=move.color)

    def draw_move_charge_bars(self):
        if self.player.charging_move or self.player.charged_move:
            moves = self.player.get_charge_moves()
            for move_index, move in enumerate(moves):
                filled_width = (move.charge_fraction) * 100
                arcade.draw_rectangle_filled(center_x=self.left + 100,
                                            center_y=self.bottom + 270 + (move_index * BAR_SPACING),
                                            width=100,
                                            height=10,
                                            color=arcade.color.BLACK)

                arcade.draw_rectangle_filled(center_x=self.left + 100 - (50 - filled_width / 2),
                                            center_y=self.bottom + 270 + (move_index * BAR_SPACING),
                                            width=filled_width,
                                            height=10,
                                            color=move.color)

    def draw_move_refresh_circles(self):
        if self.player.refreshing_move:
            moves = self.player.get_refreshing_moves()
            for move_index, move in enumerate(moves):
                filled_radius = (move.refresh_fraction) * CIRCLE_RADIUS
                arcade.draw_circle_filled(center_x=self.left + 100,
                                        center_y=self.bottom + 320 + (move_index * BAR_SPACING) + CIRCLE_RADIUS,
                                        radius= CIRCLE_RADIUS,
                                        color=arcade.color.BLACK)

                arcade.draw_circle_filled(center_x=self.left + 100,
                                        center_y=self.bottom + 320 + (move_index * BAR_SPACING) + CIRCLE_RADIUS,
                                        radius=filled_radius,
                                        color=move.color)

    def draw_xp_bar(self):
        if self.player.at_max_rank:
            max_rank_text = arcade.Text(f"MAX RANK", start_x=self.width // 2, start_y=self.top - 70, color=arcade.color.BLACK, anchor_x="center", anchor_y="center", font_size=UI_FONT_SIZE*1.5, font_name=UI_FONT)
            max_rank_text.draw()
        else:
            filled_width = (self.player.get_xp_fraction()) * 300
            arcade.draw_rectangle_filled(center_x=self.width // 2,
                                                center_y=self.top - 70,
                                                width=300,
                                                height=20,
                                                color=arcade.color.BLACK)

            arcade.draw_rectangle_filled(center_x=self.width // 2 - 150 + filled_width / 2,
                                        center_y=self.top - 70,
                                        width=filled_width,
                                        height=20,
                                        color=arcade.color.YELLOW)

            current_rank_text = arcade.Text(f"{self.player.current_rank}", start_x=self.width // 2 - 175, start_y=self.top - 70, color=arcade.color.BLACK,anchor_x="center", anchor_y="center", font_size=UI_FONT_SIZE, font_name=UI_FONT)
            next_rank_text = arcade.Text(f"{self.player.current_rank+1}", start_x=self.width // 2 + 175, start_y=self.top - 70, color=arcade.color.BLACK, anchor_x="center", anchor_y="center", font_size=UI_FONT_SIZE, font_name=UI_FONT)
            current_rank_text.draw()
            next_rank_text.draw()

    def get_player(self):
        return self.view.game_section.player

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.game_section = GameSection(0, 0,
                                       self.window.width, self.window.height, accept_keyboard_events=True)
        self.ui_section = UISection(0, 0,
                                   self.window.width, self.window.height)

        self.sectionManager = arcade.SectionManager(self)
        self.sectionManager.add_section(self.game_section)
        self.sectionManager.add_section(self.ui_section)

        self.player = None

        self.between_levels = True
        self.between_levels_timer = 0
        self.between_levels_time = 1

        self.debug = False

    def setup(self):
        self.game_section.setup()
        self.ui_section.setup()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLUE_SAPPHIRE)

    def on_draw(self):
        arcade.start_render()

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

    def start_between_levels(self):
        self.between_levels = True
        self.between_levels_timer = 0

    def update_between_levels(self):
        if self.between_levels:
            self.between_levels_timer += DELTA_TIME
            if self.between_levels_timer > self.between_levels_time:
                self.between_levels = False
                self.handle_level_completion()
                self.between_levels_timer = 0

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
        player_pos = self.game_section.player.get_integer_position()

        debug_text = arcade.Text(f"Debug Info\nEnemies: {enemy_count}\nKitties: {kitty_count}/{kitty_count_max}\nTreats on floor: {treat_count}\nPlayer Pos: {player_pos}", start_x=20, start_y=self.window.height - 20, color=arcade.color.RED, font_size=12, anchor_x="left", anchor_y="top", multiline=True, width=256)
        debug_text.draw()
        if self.between_levels:
            between_levels_text = arcade.Text(f"Between Levels {int((self.between_levels_timer/self.between_levels_time)*100)}%", start_x=20, start_y=self.window.height - 20 - LINE_HEIGHT*4, color=arcade.color.RED, font_size=12, anchor_x="left", anchor_y="top")
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
                self.game_section.player.give_xp(10*self.game_section.current_level_id)
                self.game_section.current_level_id += 1
                self.game_section.load_level()

    @property
    def should_change_level(self):
        return not self.game_section.any_enemies and not self.between_levels and not self.game_section.any_kitties

    @property
    def completed(self):
        return not self.game_section.more_levels and not self.game_section.any_enemies and not self.game_section.any_kitties
