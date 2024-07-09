import arcade
import arcade.color
from src.sprites.player import Player
from utils.camera import HKUCamera
from src.data import controls
from pyglet.math import Vec2
from src.sprites.kitty import FollowingKitty
from src.utils.level import Level

class GameSection(arcade.Section):
    def __init__(self, left: int, bottom: int, width: int, height: int,
                 **kwargs):
        super().__init__(left, bottom, width, height,
                          **kwargs)
        self.current_level = None

        self.player_sprite = None

        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.sprint_pressed = False

        self.tile_map = None

        # Physics engine
        self.physics_engine = None

        self.camera = None


    def setup(self):
        self.player_sprite = Player(id=0)

        self.load_map("resources/maps/map.json")

        self.current_level = Level(level_id=1, player=self.player_sprite, game_section=self)
        self.current_level.load_kitties()

        self.player_sprite.center_x = self.width//2
        self.player_sprite.center_y = self.height//2


        self.scene.add_sprite("Player", self.player_sprite)
        self.scene.add_sprite_list(name = "Kitty", use_spatial_hash=True, sprite_list=self.current_level.kitties)

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite,
            walls=[
                self.scene["Wall"]
            ]
        )

        for kitty in self.scene.get_sprite_list("Kitty"):
            kitty.setup()

        self.camera = HKUCamera(self.width, self.height)


    def on_update(self, delta_time: float):

        self.update_movement()
        self.update_animation()
        self.scene.update()

        # Check if sprinting and update stamina
        self.player_sprite.sprinting = (self.sprint_pressed and not self.player_sprite.stationary)
        self.player_sprite.update_stamina(delta_time)

        self.update_camera()

        self.physics_engine.update()

    def on_draw(self):
        self.scene.draw()

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

    def update_movement_direction(self):
        self.player_sprite.velocity = Vec2(0, 0)
        if self.up_pressed:
            self.player_sprite.velocity += Vec2(0, 1)
        if self.down_pressed:
            self.player_sprite.velocity -= Vec2(0, 1)
        if self.left_pressed:
            self.player_sprite.velocity -= Vec2(1, 0)
        if self.right_pressed:
            self.player_sprite.velocity += Vec2(1, 0)

    def update_movement_speed(self):
        if self.player_sprite.stamina > 0:
            if self.sprint_pressed:
                self.player_sprite.speed = self.player_sprite.base_speed * self.player_sprite.sprint_multiplier
            else:
                self.player_sprite.speed = self.player_sprite.base_speed
        else:
            self.player_sprite.speed = self.player_sprite.base_speed

    def update_movement(self):
        self.update_movement_direction()
        self.player_sprite.velocity = self.player_sprite.velocity.normalize()
        self.update_movement_speed()

        self.player_sprite.velocity = self.player_sprite.velocity.scale(self.player_sprite.speed)
        self.player_sprite.velocity = [self.player_sprite.velocity.x, self.player_sprite.velocity.y]

    def update_animation(self):
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
        player_position_for_cam = Vec2(self.player_sprite.center_x-(self.width//2), self.player_sprite.center_y-(self.height//2))
        self.camera.move_to(player_position_for_cam)
        self.camera.use()

    def load_map(self, map_path):
        layer_options = {
            "Walls": {
                "use_spatial_hash": True
            }
        }

        self.tile_map = arcade.load_tilemap(map_path, layer_options=layer_options)

        self.scene = arcade.Scene.from_tilemap(self.tile_map)

    @property
    def map_bounds(self):
        return (self.tile_map.width * self.tile_map.tile_width, self.tile_map.height * self.tile_map.tile_height)

class UISection(arcade.Section):
    def __init__(self, left: int, bottom: int, width: int, height: int, **kwargs):
        super().__init__(left, bottom, width, height,
                          **kwargs)
        self.player = None
        self.camera = None

    def setup(self):
        self.player = self.get_player()
        self.camera = arcade.Camera(self.width, self.height)

    def on_update(self, delta_time: float):
        pass

    def on_draw(self):
        self.camera.use()
        self.draw_stamina_bar()

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

    def on_update(self, delta_time: float):
        self.game_section.on_update(delta_time)
        self.ui_section.on_update(delta_time)

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
