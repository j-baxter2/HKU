import arcade
import random
from pyglet.math import Vec2
from src.data.constants import DELTA_TIME, MAP_WIDTH, MAP_HEIGHT, SOUND_EFFECT_VOL
from src.utils.sound import load_sound, play_sound
from src.sprites.moving_sprite import MovingSprite

class LivingSprite(MovingSprite):
    def __init__(self, data: dict):
        self.data = data
        super().__init__(self.data)
        self.walk_cycle_frames = self.animation_data["walk"]

        self.sprint_multiplier = data["sprint multiplier"]

        self.damage_resist = 0

        self.just_been_hit = False
        self.just_been_hit_timer = 0
        self.just_been_hit_time = 0.5

        self.just_been_healed = False
        self.just_been_healed_timer = 0
        self.just_been_healed_time = 0.5

        self.hurt_sound = load_sound("hurt1")

    def update(self):
        self.update_just_been_hit()
        self.update_just_been_healed()
        super().update()

    def update_movement_speed(self):
        if self.should_sprint:
            self.speed = self.sprint_multiplier * self.base_speed
        else:
            self.speed = self.base_speed

    def start_walk_cycle(self, direction: str):
        if direction == "up":
            self.play_animation(*self.walk_cycle_frames["up"])
        elif direction == "down":
            self.play_animation(*self.walk_cycle_frames["down"])
        elif direction == "left":
            self.play_animation(*self.walk_cycle_frames["left"])
        elif direction == "right":
            self.play_animation(*self.walk_cycle_frames["right"])

    def start_just_been_hit(self):
        self.just_been_hit = True
        self.just_been_hit_timer = 0
        play_sound(self.hurt_sound, volume=SOUND_EFFECT_VOL)

    def update_just_been_hit(self):
        if self.just_been_hit:
            self.color = arcade.color.RED
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

    def take_damage(self, amount: int):
        self.hp -= amount * (1-self.damage_resist)
        self.hp = min(max(0, self.hp), self.max_hp)
        if self.hp <= 0:
            self.stop_moving()
            self.color = self.fade_color
            self.start_fade()

    def give_xp(self, amount):
        pass

    def draw_hp_bar(self):
        arcade.draw_rectangle_filled(self.center_x, self.center_y + self.height//2 - 10, self.width, 5, arcade.color.BLACK)
        arcade.draw_rectangle_filled(self.center_x, self.center_y + self.height//2 - 10, self.width * (self.hp/self.max_hp), 5, arcade.color.RED)

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
    def fps(self):
        if self.should_sprint:
            return self.base_fps * (1 + int(self.should_sprint))
        else:
            return self.base_fps
