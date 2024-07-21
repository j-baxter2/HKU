import arcade
import json
from src.sprites.following_sprite import MovingSprite
from src.sprites.player import Player
from pyglet.math import Vec2
import random
import math
import json
from src.data.constants import MAP_WIDTH, MAP_HEIGHT, DELTA_TIME

class Kitty(MovingSprite):
    def __init__(self, id : int, treats: arcade.SpriteList):
        with open("resources/data/kitty.json", "r") as file:
            kitty_dict = json.load(file)
        self.kitty_data = kitty_dict[str(id)]

        super().__init__(self.kitty_data)

        self.treats = treats

        self.hunger = self.kitty_data["hunger"]
        self.treats_eaten = 0

        self.follow_distance = self.kitty_data["follow radius"]
        self.follow_speed_bonus = self.kitty_data["follow speed bonus"]

        self.change_direction_time = self.kitty_data["change direction time"]
        self.random_movement_timer = 0

        self.velocity = Vec2(0, 0)

        self.target_treat = None

        self.fading = False
        self.fade_timer = 0
        self.fade_time = 1

        self.eating = False
        self.eating_timer = 0
        self.eating_time = 1

    def setup(self):
        self.randomize_velocity()

    def update(self):
        if self.fading:
            self.update_fade()
        else:
            if self.able_to_move:
                self.update_movement()
            self.random_movement_timer += DELTA_TIME
            self.locate_treat()
            self.update_animation(delta_time = DELTA_TIME)
            self.handle_treat_collision()
            self.update_eating()
            super().update()

    def update_fade(self):
        self.fade_timer += DELTA_TIME
        opacity_decrease = 255 * (self.fade_timer / 2)
        self.alpha = max(255 - opacity_decrease, 0)
        if self.fade_timer >= self.fade_time:
            self.fading = False
            self.kill()

    def start_eating(self):
        self.eating = True

    def update_eating(self):
        if self.eating:
            self.eating_timer += DELTA_TIME
            if self.eating_timer >= self.eating_time:
                self.stop_eating()

    def stop_eating(self):
        self.eating = False
        self.eating_timer = 0
        self.target_treat.kill()
        self.target_treat = None
        self.treats_eaten += 1
        if self.treats_eaten >= self.hunger:
            self.fading = True


    def update_movement_direction(self):
        if self.target_treat:
            self.face_treat()
        elif self.should_turn:
            self.randomize_velocity()
            self.random_movement_timer = 0

    def update_movement_speed(self):
        if self.target_treat:
            self.speed = self.follow_speed_bonus * self.base_speed
        else:
            self.speed = self.base_speed

    def update_movement(self):
        self.update_movement_direction()
        self.velocity = Vec2(self.velocity[0], self.velocity[1])
        self.velocity = self.velocity.normalize()
        self.update_movement_speed()

        self.velocity = self.velocity.scale(self.speed)

        self.velocity = [self.velocity.x, self.velocity.y]

        self.handle_out_of_bounds()

    def handle_out_of_bounds(self):
        if self.center_x < 0 or self.center_x > MAP_WIDTH:
            self.velocity = [self.velocity[0] * -1, self.velocity[1]]
        elif self.center_y < 0 or self.center_y > MAP_HEIGHT:
            self.velocity = [self.velocity[0], self.velocity[1] * -1]

    def handle_treat_collision(self):
        if self.target_treat:
            if arcade.check_for_collision(self, self.target_treat):
                self.start_eating()

    @property
    def animation_direction(self):
        self.velocity = Vec2(self.velocity[0], self.velocity[1])
        angle = self.velocity.heading
        angle = math.degrees(angle)
        if angle < 135 and angle >= 45:
            return "up"
        elif angle < 45 and angle >= -45:
            return "right"
        elif angle < -45 and angle >= -135:
            return "down"
        else:
            return "left"

    def update_animation(self, delta_time):
        if not self.current_walk_cycle:
            if self.animation_direction:
                self.start_walk_cycle(self.animation_direction)
                self.hit_box = self.texture.hit_box_points
        self.advance_walk_cycle()

    def draw_follow_radius(self):
        arcade.draw_circle_outline(self.center_x, self.center_y, self.follow_distance, arcade.color.BLUE, 8)

    @property
    def should_turn(self):
        return self.random_movement_timer >= (self.change_direction_time+random.uniform(-0.1, 5))

    def face_treat(self):
        self.velocity = Vec2(self.target_treat.center_x - self.center_x, self.target_treat.center_y - self.center_y)

    def locate_treat(self):
        for treat in self.treats:
            if arcade.get_distance_between_sprites(self, treat) < self.follow_distance:
                self.target_treat = treat
            else:
                self.target_treat = None
