import arcade
from src.sprites.living_sprite import LivingSprite
from src.sprites.player import Player
from pyglet.math import Vec2
import random
import math
import json
from src.data.constants import MAP_WIDTH, MAP_HEIGHT, DELTA_TIME, M, SOUND_EFFECT_VOL

class FollowingSprite(LivingSprite):
    def __init__(self, data: dict, scene: arcade.Scene):
        self.scene = scene
        self.player = self.scene.get_sprite_list("Player")[0]
        self.follow_distance = data["follow radius"]
        self.random_movement_time = data["random movement time"]
        self.fade_texture_index = data["spritesheet"]["fade texture"]
        self.random_movement_timer = 0
        self.in_ocean = False
        super().__init__(scene, data)

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
            self.update_ocean()
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

    def update_ocean(self):
        ocean = self.scene.get_sprite_list("Ocean")
        if arcade.check_for_collision_with_list(self, sprite_list=ocean):
            self.in_ocean = True
            self.speed_multiplier = 0.5
            self.current_movement_frames = self.swim_cycle_frames
            self.start_walk_cycle(self.animation_direction)
        else:
            self.in_ocean = False
            self.speed_multiplier = 1
            self.current_movement_frames = self.walk_cycle_frames
            self.start_walk_cycle(self.animation_direction)

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

    def apparent_player_position(self, vision=0.0):
        true_player_position = self.player.position
        distance = arcade.get_distance_between_sprites(self, self.player)
        apparent_player_position = (true_player_position[0] + random.uniform(-distance*(1-vision), distance*(1-vision)), true_player_position[1] + random.uniform(-distance*(1-vision), distance*(1-vision)))
        return apparent_player_position

    def get_volume_from_player_pos(self):
        distance = arcade.get_distance_between_sprites(self, self.player)
        distance_in_m = distance / M
        if distance == 0:
            volume = 1
        else:
            volume = 1/(distance_in_m)
        return min(max(volume, 0)*SOUND_EFFECT_VOL*(arcade.get_window().sfx_vol), 1)

    def get_pan_from_player_pos(self):
        angle = arcade.get_angle_radians(self.player.center_x, self.player.center_y, self.center_x, self.center_y)
        return math.sin(angle)

    @property
    def should_turn(self):
        return self.random_movement_timer >= (self.random_movement_time+random.uniform(-0.1, 5))

    @property
    def can_attack(self):
        return not self.just_attacked

    @property
    def should_sprint(self):
        return self.just_been_hit

    def draw_follow_radius(self):
        arcade.draw_circle_outline(self.center_x, self.center_y, self.follow_distance, arcade.color.BLUE, 8)

    def draw_debug(self):
        super().draw_debug()
        self.draw_follow_radius()
