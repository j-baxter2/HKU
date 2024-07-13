import arcade
import arcade.color
from src.sprites.player import Player
from utils.camera import HKUCamera
from src.data import controls
from pyglet.math import Vec2
from src.sprites.kitty import FollowingKitty
from src.utils.move import Move
from src.utils.level import Level
from src.data.constants import MAP_WIDTH, MAP_HEIGHT, DELTA_TIME

class GameSection(arcade.Section):
    def __init__(self, left: int, bottom: int, width: int, height: int,
                 **kwargs):
        super().__init__(left, bottom, width, height,
                          **kwargs)
        self.current_level = None

        self.player_sprite = None
        self.player_sprite_list = arcade.SpriteList()

        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.sprint_pressed = False

        self.tile_map = None

        self.physics_engine = None

        self.camera = None


    def setup(self):
        self.player_sprite = Player(id=1)
        self.player_sprite_list.append(self.player_sprite)


        self.load_map("resources/maps/map.json")

        self.current_level = Level(level_id=1, player=self.player_sprite, game_section=self)
        self.current_level.load_kitties()
        self.current_level.spawn_player()

        self.scene.add_sprite_list(name = "Kitty", sprite_list=self.current_level.kitties, use_spatial_hash=True)
        self.scene.add_sprite_list(name="Player",sprite_list=self.player_sprite_list, use_spatial_hash=True)

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite,
            walls=[
                self.scene["Wall"]
            ]
        )

        for kitty in self.scene.get_sprite_list("Kitty"):
            kitty.setup()

        # Set up player moves
        basic_attack = Move(0, self.scene, self.player_sprite)
        self.player_sprite.add_move(basic_attack)
        basic_heal = Move(1, self.scene, self.player_sprite)
        self.player_sprite.add_move(basic_heal)

        self.camera = HKUCamera(self.width, self.height)

    def on_update(self):
        if self.player_sprite.fading:
            self.player_sprite.update_fade()
        else:
            self.update_player()
        self.scene.update(["Kitty"])
        self.update_camera()
        self.physics_engine.update()

    def on_draw(self):
        self.scene.draw()
        for move in self.player_sprite.move_set:
            if move.active:
                move.draw()

    def on_key_press(self, key, modifiers):
        if key == controls.UP:
            self.up_pressed = True
        elif key == controls.DOWN:
            self.down_pressed = True
        elif key == controls.LEFT:
            self.left_pressed = True
        elif key == controls.RIGHT:
            self.right_pressed = True
        elif key == controls.SPRINT:
            self.sprint_pressed = True
        elif key == controls.ATTACK:
            self.player_sprite.do_move("basic pat")
        elif key == controls.HEAL:
            self.player_sprite.start_charging_move("basic heal")

    def on_key_release(self, key, modifiers):
        if key == controls.UP:
            self.up_pressed = False
        elif key == controls.DOWN:
            self.down_pressed = False
        elif key == controls.LEFT:
            self.left_pressed = False
        elif key == controls.RIGHT:
            self.right_pressed = False
        elif key == controls.SPRINT:
            self.sprint_pressed = False
        elif key == controls.HEAL:
            self.player_sprite.stop_charging_move("basic heal")

    def update_player(self):
        self.update_player_movement()
        self.update_player_animation()
        self.player_sprite.update()
        self.update_sprinting_flag()
        self.player_sprite.update_stamina(DELTA_TIME)
        self.update_moves()

    def update_player_movement(self):
        self.update_player_movement_direction()
        self.update_player_movement_speed()

        self.player_sprite.velocity = [self.player_sprite.velocity.x, self.player_sprite.velocity.y]

        self.player_sprite.center_x = max(0, min(self.player_sprite.center_x, MAP_WIDTH))
        self.player_sprite.center_y = max(0, min(self.player_sprite.center_y, MAP_HEIGHT))

    def update_player_movement_direction(self):
        self.player_sprite.velocity = Vec2(0, 0)
        if self.up_pressed:
            self.player_sprite.velocity += Vec2(0, 1)
        if self.down_pressed:
            self.player_sprite.velocity -= Vec2(0, 1)
        if self.left_pressed:
            self.player_sprite.velocity -= Vec2(1, 0)
        if self.right_pressed:
            self.player_sprite.velocity += Vec2(1, 0)

        self.player_sprite.velocity = self.player_sprite.velocity.normalize()

    def update_player_movement_speed(self):
        if self.player_sprite.stamina > 0:
            if self.sprint_pressed:
                self.player_sprite.speed = self.player_sprite.base_speed * self.player_sprite.sprint_multiplier
            else:
                self.player_sprite.speed = self.player_sprite.base_speed
        else:
            self.player_sprite.speed = self.player_sprite.base_speed
        self.player_sprite.velocity = self.player_sprite.velocity.scale(self.player_sprite.speed)

    def update_moves(self):
        for move in self.player_sprite.move_set:
                    move.on_update(DELTA_TIME)

    def update_sprinting_flag(self):
        self.player_sprite.sprinting = (self.sprint_pressed and not self.player_sprite.stationary)

    def update_player_animation(self):
        if not self.player_sprite.current_walk_cycle:
            if self.up_pressed:
                self.player_sprite.start_walk_cycle('up')
            elif self.down_pressed:
                self.player_sprite.start_walk_cycle('down')
            elif self.left_pressed:
                self.player_sprite.start_walk_cycle('left')
            elif self.right_pressed:
                self.player_sprite.start_walk_cycle('right')
        self.player_sprite.advance_walk_cycle()

    def update_camera(self):
        if self.player_sprite.is_alive:
            player_position_for_cam = Vec2(self.player_sprite.center_x-(self.width//2), self.player_sprite.center_y-(self.height//2))
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

class UISection(arcade.Section):
    def __init__(self, left: int, bottom: int, width: int, height: int, **kwargs):
        super().__init__(left, bottom, width, height,
                          **kwargs)
        self.player = None
        self.camera = None

    def setup(self):
        self.player = self.get_player()
        self.camera = arcade.Camera(self.width, self.height)

    def on_update(self):
        pass

    def on_draw(self):
        self.camera.use()
        if not self.player.faded:
            self.draw_stamina_bar()
            self.draw_hp_bar()
            self.draw_move_activity_bar()
            self.draw_move_charge_bar()

        self.view.game_section.camera.use()
        self.view.game_section.player_sprite.draw()

    def draw_stamina_bar(self):
        if self.player:
            # Calculate the width of the filled portion of the stamina bar
            filled_width = (self.player.stamina / self.player.max_stamina) * 100
            # Draw the background of the stamina bar
            arcade.draw_rectangle_filled(center_x=self.left + 100,
                                         center_y=self.bottom + 70,
                                         width=100,
                                         height=10,
                                         color=arcade.color.BLACK)
            # Draw the filled portion of the stamina bar
            arcade.draw_rectangle_filled(center_x=self.left + 100 - (50 - filled_width / 2),
                                         center_y=self.bottom + 70,
                                         width=filled_width,
                                         height=10,
                                         color=arcade.color.GREEN)

    def draw_hp_bar(self):
        if self.player:
            # Calculate the width of the filled portion of the hp bar
            filled_width = (self.player.hp / self.player.max_hp) * 100
            # Draw the background of the hp bar
            arcade.draw_rectangle_filled(center_x=self.left + 100,
                                         center_y=self.bottom + 120,
                                         width=100,
                                         height=10,
                                         color=arcade.color.BLACK)
            # Draw the filled portion of the hp bar
            arcade.draw_rectangle_filled(center_x=self.left + 100 - (50 - filled_width / 2),
                                         center_y=self.bottom + 120,
                                         width=filled_width,
                                         height=10,
                                         color=arcade.color.RED)

    def draw_move_activity_bar(self):
        if self.player.doing_move:
            move = self.player.get_active_move()
            # Calculate the width of the filled portion of the move status bar
            filled_width = (move.progress_fraction) * 100
            # Draw the background of the move status bar
            arcade.draw_rectangle_filled(center_x=self.left + 100,
                                         center_y=self.bottom + 220,
                                         width=100,
                                         height=10,
                                         color=arcade.color.BLACK)
            # Draw the filled portion of the move status bar
            arcade.draw_rectangle_filled(center_x=self.left + 100 - (50 - filled_width / 2),
                                         center_y=self.bottom + 220,
                                         width=filled_width,
                                         height=10,
                                         color=move.color)

    def draw_move_charge_bar(self):
        if self.player.charging_move:
            move = self.player.get_charging_move()
            # Calculate the width of the filled portion of the move status bar
            filled_width = (move.charge_fraction) * 100
            # Draw the background of the move status bar
            arcade.draw_rectangle_filled(center_x=self.left + 100,
                                         center_y=self.bottom + 270,
                                         width=100,
                                         height=10,
                                         color=arcade.color.BLACK)
            # Draw the filled portion of the move status bar
            arcade.draw_rectangle_filled(center_x=self.left + 100 - (50 - filled_width / 2),
                                         center_y=self.bottom + 270,
                                         width=filled_width,
                                         height=10,
                                         color=move.color)

    def get_player(self):
        return self.view.game_section.player_sprite

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

        self.player_sprite = None

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

        if self.debug:
            self.debug_draw()

        self.handle_endgame_messages()

    def on_update(self, delta_time=DELTA_TIME):
        self.game_section.on_update()
        self.ui_section.on_update()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.APOSTROPHE:
            self.debug = not self.debug

        self.game_section.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        self.game_section.on_key_release(key, modifiers)

    def debug_draw(self):
        self.ui_section.camera.use()

        arcade.draw_text("Debug Mode", self.window.width - 100, self.window.height - 20, arcade.color.RED, 12)
        kitty_count = len(self.game_section.scene.get_sprite_list("Kitty"))
        arcade.draw_text(f"Kitties: {kitty_count}", self.window.width - 100, self.window.height - 40, arcade.color.RED, 12)
        player_pos = self.game_section.player_sprite.get_integer_position()
        arcade.draw_text(f"Player Pos: {player_pos}", self.window.width - 200, self.window.height - 60, arcade.color.RED, 12)

        self.game_section.camera.use()
        self.game_section.player_sprite.debug_draw()
        kitties = self.game_section.scene.get_sprite_list("Kitty")
        for kitty in kitties:
            kitty.debug_draw()

    def draw_victory_message(self):
        arcade.draw_text("Congrats, you snuggled all the kitties <3", self.game_section.player_sprite.center_x, self.game_section.player_sprite.center_y+100, arcade.color.PURPLE, 24)

    def draw_defeat_message(self):
        arcade.draw_text("You have been defeated by cuteness", self.window.width//2, self.window.height//2, arcade.color.PURPLE, 24, anchor_x="center", anchor_y="center")

    def handle_endgame_messages(self):
        if len(self.game_section.scene.get_sprite_list("Kitty")) == 0:
            self.draw_victory_message()
        elif self.game_section.player_sprite.hp <= 0:
            self.draw_defeat_message()
