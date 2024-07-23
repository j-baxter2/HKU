import arcade
from src.sprites.moving_sprite import MovingSprite
from src.sprites.player import Player
from pyglet.math import Vec2
import random
import math
import json
from src.data.constants import MAP_WIDTH, MAP_HEIGHT, DELTA_TIME

class FollowingSprite(MovingSprite):
    def __init__(self, data: dict, player: Player):
        self.player = player
        self.follow_distance = data["follow radius"]
        self.random_movement_time = data["random movement time"]
        self.random_movement_timer = 0
        super().__init__(data)

    def setup(self):
        self.randomize_velocity()

    def update(self):
        super().update()
        if self.fading:
            self.update_fade()
        else:
            if self.able_to_move:
                self.update_movement()
            self.random_movement_timer += DELTA_TIME
            self.update_animation(delta_time = DELTA_TIME)
            self.update_while_alive()

    def update_fade(self):
        super().update_fade()

    def update_while_alive(self):
        pass

    def update_movement_direction(self):
        if self.should_turn:
            self.randomize_velocity()

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

    def handle_player_collision(self):
       if self.can_attack and arcade.check_for_collision(self, self.player):
           self.player.take_damage(self.attack)
           self.just_attacked = True
           self.player.just_been_hit = True

    def face_player(self):
        self.velocity = Vec2(self.player.center_x - self.center_x, self.player.center_y - self.center_y)

    @property
    def should_turn(self):
        return self.random_movement_timer >= (self.random_movement_time+random.uniform(-0.1, 5))

    @property
    def can_attack(self):
        return not self.just_attacked

    @property
    def should_sprint(self):
        return self.just_been_hit

    def debug_draw(self):
        super().debug_draw()
        self.draw_follow_radius()
        arcade.draw_text(f"RMT: {round(self.random_movement_timer,1)}", self.center_x, self.top + 60, arcade.color.RED, 12)
        if hasattr(self, "hp"):
            arcade.draw_text(f"HP: {self.hp}", self.center_x, self.top + 120, arcade.color.RED, 12)
        arcade.draw_text(f"JBH: {self.just_been_hit}", self.center_x, self.center_y+100, arcade.color.WHITE, 20)
