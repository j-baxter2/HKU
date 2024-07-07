import arcade
from src.sprites.moving_sprite import MovingSprite
from src.sprites.player import Player
from pyglet.math import Vec2
import numpy as np
import json

class FollowingKitty(MovingSprite):
    def __init__(self, id : int, player : Player):
        # Load player data from JSON
        with open("resources/data/kitty.json", "r") as file:
            kitty_dict = json.load(file)
        self.kitty_data = kitty_dict[str(id)]

        self.player = player
        self.follow_distance = self.kitty_data["follow radius"]
        self.follow_speed_bonus = self.kitty_data["follow speed bonus"]
        super().__init__(self.kitty_data)

    @property
    def in_range(self):
        return arcade.get_distance_between_sprites(self, self.player) < self.follow_distance

    def update_movement_direction(self):
        #todo: implement treats taking priority over player
        if self.in_range:
            self.velocity = Vec2(self.player.center_x - self.center_x, self.player.center_y - self.center_y)
        else:
            #set movement direction to random
            random_direction_x = np.random.uniform(-1, 1)
            random_direction_y = np.random.uniform(-1, 1)
            self.velocity = Vec2(random_direction_x, random_direction_y)

    @property
    def animation_direction(self):
        #get the angle of the velocity vector
        self.velocity = Vec2(self.velocity[0], self.velocity[1])
        angle = self.velocity.heading
        #convert the angle to degrees
        angle = np.degrees(angle)
        if angle < 135 and angle >= 45:
            return "up"
        elif angle < 45 and angle >= -45:
            return "right"
        elif angle < -45 and angle >= -135:
            return "down"
        else:
            return "left"

    def update_movement_speed(self):
        if self.in_range:
            self.speed = self.follow_speed_bonus * self.base_speed
        else:
            self.speed = self.base_speed

    def update_movement(self):
        self.update_movement_direction()
        self.velocity = self.velocity.normalize()
        self.update_movement_speed()

        self.velocity = self.velocity.scale(self.speed)
        self.velocity = [self.velocity.x, self.velocity.y]

    def update_animation(self, delta_time):
        if not self.current_walk_cycle:
            if self.animation_direction:
                self.start_walk_cycle(self.animation_direction)
                self.hit_box = self.texture.hit_box_points
        self.advance_walk_cycle()

    def update(self, delta_time = 1/60):
        self.update_movement()
        self.update_animation(delta_time)
        super().update()

    def draw_follow_radius(self):
        arcade.draw_circle_outline(self.center_x, self.center_y, self.follow_distance, arcade.color.BLUE, 2)

    def debug_draw(self):
        self.draw_follow_radius()
        super().debug_draw()
