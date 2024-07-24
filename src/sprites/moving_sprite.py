import arcade
import random
from pyglet.math import Vec2
from src.data.constants import DELTA_TIME, MAP_WIDTH, MAP_HEIGHT, SOUND_EFFECT_VOL
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

        self.fade_texture_index = None

        if self.textures:
            self.set_texture(0)


        self._hit_box_algorithm = 'Simple'
        self.set_hit_box(self.texture.hit_box_points)

        animation_data = data["animation"]

        self.current_walk_cycle = None

        self.animation_timer = 0
        self.base_fps = animation_data["fps"]
        self.base_frame_time = 1 / self.base_fps
        self.walk_cycle_frames = animation_data["walk"]

        self.able_to_move = True
        self.base_speed = data["speed"]
        self.sprint_multiplier = data["sprint multiplier"]
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
        if self.should_sprint:
            self.speed = self.sprint_multiplier * self.base_speed
        else:
            self.speed = self.base_speed

    def handle_out_of_bounds(self):
        if self.center_x < 0 or self.center_x > MAP_WIDTH:
            self.velocity = [self.velocity[0] * -1, self.velocity[1]]
        elif self.center_y < 0 or self.center_y > MAP_HEIGHT:
            self.velocity = [self.velocity[0], self.velocity[1] * -1]
        self.center_x = max(0, min(self.center_x, MAP_WIDTH))
        self.center_y = max(0, min(self.center_y, MAP_HEIGHT))

    def update_just_been_hit(self):
        if self.just_been_hit:
            self.color = arcade.color.RED
            play_sound(self.hurt_sound, volume=SOUND_EFFECT_VOL)
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
            self.start_fade()

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

    @property
    def should_sprint(self):
        return self.just_been_hit

    @property
    def should_turn(self):
        return False

    @property
    def fps(self):
        if self.should_sprint:
            return self.base_fps * (1 + int(self.should_sprint))
        else:
            return self.base_fps

    @property
    def frame_time(self):
        return 1 / self.fps

    def debug_draw(self):
        self.draw_hit_box()
