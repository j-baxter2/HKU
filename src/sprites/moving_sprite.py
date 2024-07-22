import arcade
import random
from pyglet.math import Vec2
from src.data.constants import DELTA_TIME
from src.utils.sound import load_sound, play_sound

class MovingSprite(arcade.Sprite):
    def __init__(self, data: dict):

        sprite_data = data["spritesheet"]

        sheet_path = sprite_data["path"]
        scale = sprite_data["scale"]

        super().__init__(sheet_path, scale)

        columns = sprite_data["columns"]
        count = sprite_data["count"]
        width = sprite_data["width"]
        height = sprite_data["height"]

        self.textures = arcade.load_spritesheet(
            sheet_path,
            sprite_width=width,
            sprite_height=height,
            columns=columns,
            count=count,
        )

        if self.textures:
            self.set_texture(0)


        self._hit_box_algorithm = 'Simple'
        self.set_hit_box(self.texture.hit_box_points)


        animation_data = data["animation"]

        self.current_walk_cycle = None

        self.animation_timer = 0
        self.fps = animation_data["fps"]
        self.frame_time = 1 / self.fps
        self.walk_cycle_frames = animation_data["walk"]

        self.able_to_move = True
        self.base_speed = data["speed"]
        self.speed = 0

        self.damage_resist = 0

        self.fading = False
        self.fade_timer = 0
        self.fade_time = 3

        self.faded = False
        self.fade_color_key = data["fade color"]
        self.fade_color = getattr(arcade.color, self.fade_color_key.upper())

        self.just_been_hit = False
        self.just_been_hit_timer = 0
        self.just_been_hit_time = 0.5

        self.just_been_healed = False
        self.just_been_healed_timer = 0
        self.just_been_healed_time = 0.5

        self.hurt_sound = load_sound("hurt2")

    def walk_cycle(self, starting_frame: int, ending_frame: int):
        if self.textures:
            self.set_texture(starting_frame)
        for i in range(starting_frame, ending_frame + 1):
            self.set_texture(i)
            yield

    def start_walk_cycle(self, direction: str):
        starting_frame, ending_frame = self.walk_cycle_frames[direction]
        self.current_walk_cycle = self.walk_cycle(starting_frame, ending_frame)
        self.animation_timer = 0

    def advance_walk_cycle(self, delta_time=DELTA_TIME):
        self.animation_timer += delta_time

        if self.animation_timer >= self.frame_time:
            self.animation_timer -= self.frame_time

            if self.current_walk_cycle:
                try:
                    next(self.current_walk_cycle)
                except StopIteration:
                    self.current_walk_cycle = None

    def update(self):
        self.update_just_been_hit()
        self.update_just_been_healed()
        super().update()

    def update_fade(self):
        self.fade_timer += DELTA_TIME
        opacity_decrease = 255 * (self.fade_timer / 2)
        self.alpha = max(255 - opacity_decrease, 0)
        if self.fade_timer >= self.fade_time:
            self.fading = False
            self.kill()

    def update_just_been_hit(self):
        if self.just_been_hit:
            self.color = arcade.color.RED
            #play_sound(self.hurt_sound)
            self.just_been_hit_timer += DELTA_TIME
            if self.just_been_hit_timer >= self.just_been_hit_time:
                self.stop_just_been_hit()

    def stop_just_been_hit(self):
        self.just_been_hit = False
        self.just_been_hit_timer = 0
        self.color = arcade.color.WHITE

    def update_just_been_healed(self):
        if self.just_been_healed:
            self.color = arcade.color.GREEN
            self.just_been_healed_timer += DELTA_TIME
            if self.just_been_healed_timer >= self.just_been_healed_time:
                self.stop_just_been_healed()

    def stop_just_been_healed(self):
        self.just_been_healed = False
        self.just_been_healed_timer = 0
        self.color = arcade.color.WHITE

    @property
    def stationary(self):
        if self.velocity == [0, 0] or self.velocity == Vec2(0, 0):
            return True
        else:
            return False


    def randomize_velocity(self):
        if isinstance(self.velocity, list):
            self.velocity = [random.uniform(-1, 1), random.uniform(-1,1)]
        elif isinstance(self.velocity, Vec2):
            self.velocity = Vec2(random.uniform(-1, 1), random.uniform(-1,1))

    def take_damage(self, amount: int):
        self.hp -= amount * (1-self.damage_resist)
        self.hp = min(max(0, self.hp), self.max_hp)
        if self.hp <= 0:
            self.stop_moving()
            self.color = self.fade_color
            self.fading = True

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
    def is_alive(self):
        return not self.faded

    @property
    def is_dead(self):
        return self.hp <= 0

    def debug_draw(self):
        self.draw_hit_box()
