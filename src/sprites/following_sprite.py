import arcade
from src.sprites.living_sprite import LivingSprite
from src.sprites.player import Player
from pyglet.math import Vec2
import random
import math
import json
from src.data.constants import MAP_WIDTH, MAP_HEIGHT, DELTA_TIME

class FollowingSprite(LivingSprite):
    def __init__(self, data: dict, scene: arcade.Scene):
        self.scene = scene
        self.player = self.scene.get_sprite_list("Player")[0]
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
            self.update_player()
            self.update_while_alive()

    def update_player(self):
        try:
            self.player = self.scene.get_sprite_list("Player")[0]
        except IndexError:
            pass

    def update_fade(self):
        super().update_fade()

    def update_while_alive(self):
        pass

    def update_movement_direction(self):
        if self.should_turn:
            self.randomize_velocity()
            self.random_movement_timer = 0

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
        if not self.current_animation:
            if self.animation_direction:
                self.start_walk_cycle(self.animation_direction)
                self.hit_box = self.texture.hit_box_points
        self.advance_animation()


    def draw_follow_radius(self):
        arcade.draw_circle_outline(self.center_x, self.center_y, self.follow_distance, arcade.color.BLUE, 8)

    def handle_player_collision(self):
       if self.can_attack and arcade.check_for_collision(self, self.player):
           self.player.take_damage(self.attack)
           self.just_attacked = True
           self.paralyze()
           self.player.just_been_hit = True

    def start_fleeing(self):
        self.fleeing = True
        self.fleeing_timer = 0
        #play scared sound

    def update_fleeing(self):
        if self.fleeing:
            self.fleeing_timer += DELTA_TIME
            if self.fleeing_timer >= self.fleeing_time:
                self.fleeing = False
                self.fleeing_timer = 0

    def face(self, position):
        self.velocity = Vec2(position[0] - self.center_x, position[1] - self.center_y)

    def face_away(self, position):
        self.velocity = Vec2(self.center_x - position[0], self.center_y - position[1])

    def apparent_player_position(self, vision=0.0):
        true_player_position = self.player.position
        distance = arcade.get_distance_between_sprites(self, self.player)
        apparent_player_position = (true_player_position[0] + random.uniform(-distance*(1-vision), distance*(1-vision)), true_player_position[1] + random.uniform(-distance*(1-vision), distance*(1-vision)))
        return apparent_player_position

    @property
    def should_turn(self):
        return self.random_movement_timer >= (self.random_movement_time+random.uniform(-0.1, 5))

    @property
    def can_attack(self):
        return not self.just_attacked

    @property
    def should_sprint(self):
        return self.just_been_hit

    def draw_debug(self):
        super().draw_debug()
        self.draw_follow_radius()
