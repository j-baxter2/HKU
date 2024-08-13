import arcade
import random
from pyglet.math import Vec2
from src.data.constants import DELTA_TIME, MAP_WIDTH, MAP_HEIGHT, SOUND_EFFECT_VOL, TILE_SIZE
from src.utils.sound import load_sound, play_sound

class MovingSprite(arcade.Sprite):
    def __init__(self, data: dict):

        sprite_data = data["spritesheet"]

        sheet_path = sprite_data["path"]
        tile_scale = sprite_data["scale"]


        columns = sprite_data["columns"]
        count = sprite_data["count"]
        width = sprite_data["width"]
        height = sprite_data["height"]

        # Calculate scale using the formula
        true_scale = (tile_scale * 128) / max(width, height)

        super().__init__(sheet_path, true_scale)

        self.textures = arcade.load_spritesheet(
            sheet_path,
            sprite_width=width,
            sprite_height=height,
            columns=columns,
            count=count,
        )

        self.fade_texture_index = None

        if self.textures:
            self.set_texture(0)

        self._hit_box_algorithm = 'Simple'
        self.set_hit_box(self.texture.hit_box_points)

        self.animation_data = data["animation"]

        self.current_animation = None

        self.animation_timer = 0
        self.base_fps = self.animation_data["fps"]
        self.base_frame_time = 1 / self.base_fps

        self.able_to_move = True
        self.base_speed = data["speed"]
        self.speed = 0

        self.fading = False
        self.fade_timer = 0
        self.fade_time = 3

        self.faded = False
        self.fade_color_key = data["fade color"]
        self.fade_color = getattr(arcade.color, self.fade_color_key.upper())

    def animation_cycle(self, starting_frame: int, ending_frame: int, looping: bool):
        while True:
            for i in range(starting_frame, ending_frame + 1):
                self.set_texture(i)
                yield
            if not looping:
                break

    def play_animation(self, starting_frame: int, ending_frame: int, looping: bool = False):
        self.current_animation = self.animation_cycle(starting_frame, ending_frame, looping)
        self.animation_timer = 0

    def advance_animation(self):
        self.animation_timer += DELTA_TIME
        if self.animation_timer >= self.frame_time:
            self.animation_timer -= self.frame_time

            if self.current_animation:
                try:
                    next(self.current_animation)
                except StopIteration:
                    self.current_animation = None

    def stop_animation(self):
        self.current_animation = None

    def update(self):
        super().update()

    def start_fade(self):
        if self.fade_texture_index:
            self.set_texture(self.fade_texture_index)
        self.fading = True

    def update_fade(self):
        self.fade_timer += DELTA_TIME
        opacity_decrease = 255 * (self.fade_timer / 2)
        self.alpha = max(255 - opacity_decrease, 0)
        self.center_y += 1
        if self.fade_timer >= self.fade_time:
            self.fading = False
            self.faded = True
            self.kill()

    def update_movement(self):
        self.update_movement_direction()
        self.velocity = Vec2(self.velocity[0], self.velocity[1])
        self.velocity = self.velocity.normalize()
        self.update_movement_speed()
        self.velocity = self.velocity.scale(self.speed)
        self.velocity = [self.velocity.x, self.velocity.y]
        self.handle_out_of_bounds()

    def update_movement_direction(self):
        if self.should_turn:
            self.randomize_velocity()

    def update_movement_speed(self):
        self.speed = self.base_speed

    def handle_out_of_bounds(self):
        if self.center_x < 0 or self.center_x > MAP_WIDTH-1:
            self.velocity = [self.velocity[0] * -1, self.velocity[1]]
        elif self.center_y < 0 or self.center_y > MAP_HEIGHT-1:
            self.velocity = [self.velocity[0], self.velocity[1] * -1]
        self.center_x = max(1, min(self.center_x, MAP_WIDTH-1))
        self.center_y = max(1, min(self.center_y, MAP_HEIGHT-1))

    def face(self, position):
        self.velocity = Vec2(position[0] - self.center_x, position[1] - self.center_y)

    def face_away(self, position):
        self.velocity = Vec2(self.center_x - position[0], self.center_y - position[1])

    def randomize_velocity(self):
        if isinstance(self.velocity, list):
            self.velocity = [random.uniform(-1, 1), random.uniform(-1,1)]
        elif isinstance(self.velocity, Vec2):
            self.velocity = Vec2(random.uniform(-1, 1), random.uniform(-1,1))

    def start_moving(self):
        self.able_to_move = True

    def stop_moving(self):
        if isinstance(self.velocity, list):
            self.velocity = [0,0]
        elif isinstance(self.velocity, Vec2):
            self.velocity = Vec2(0,0)

    def paralyze(self):
        self.stop_moving()
        self.able_to_move = False

    @property
    def stationary(self):
        if self.velocity == [0, 0] or self.velocity == Vec2(0, 0):
            return True
        else:
            return False

    @property
    def should_turn(self):
        return False

    @property
    def frame_time(self):
        return 1 / self.fps

    @property
    def fps(self):
        return self.base_fps

    def draw_debug(self):
        self.draw_hit_box()
