import arcade
from src.sprites.enemy import BaseEnemy
from src.sprites.player import Player
from pyglet.math import Vec2
import random
import math
import json
from src.data.constants import MAP_WIDTH, MAP_HEIGHT, DELTA_TIME

class DistruptorEnemy(BaseEnemy):
    def __init__(self, id : int, scene: arcade.Scene):
        self.scene = scene
        super().__init__(id, self.scene)
        self.kitties = self.scene.get_sprite_list("Kitty")
        self.attack = self.enemy_data["attack"]
        self.just_attacked = False
        self.attack_refresh_time = 0
        self.target_kitty = None

    def setup(self):
        super().setup()

    def update_while_alive(self):
        self.look_for_eating_kitty()
        if self.target_kitty:
            self.update_target_kitty()
            self.handle_kitty_collision()
        self.handle_player_collision()
        self.update_attack_refresh()

    def update_attack_refresh(self):
        if self.just_attacked:
            self.attack_refresh_time += DELTA_TIME
            if self.attack_refresh_time >= 0.7 and not self.able_to_move:
                self.start_moving()
                self.randomize_velocity()
            elif self.attack_refresh_time >= 1:
                self.reset_attack_timer()

    def reset_attack_timer(self):
        self.just_attacked = False
        self.attack_refresh_time = 0

    def update_movement_direction(self):
        if self.target_kitty:
            self.face(self.target_kitty.position)
        elif self.in_range and not self.player.faded:
            self.face(self.apparent_player_position())
        elif self.should_turn:
            self.randomize_velocity()
            self.random_movement_timer = 0

    def face_kitty(self):
        self.velocity = Vec2(self.target_kitty.center_x - self.center_x, self.target_kitty.center_y - self.center_y)

    def look_for_eating_kitty(self):
        for kitty in self.kitties:
            if arcade.get_distance_between_sprites(self, kitty) < self.follow_distance*3 and kitty.eating:
                self.target_kitty = kitty
                break

    def update_target_kitty(self):
        if self.target_kitty.fading or self.target_kitty.faded or not self.target_kitty.eating:
            self.target_kitty = None

    def handle_kitty_collision(self):
        if self.target_kitty:
            if self.can_attack and arcade.check_for_collision(self, self.target_kitty):
                self.target_kitty.start_fleeing()
                #play roar
                self.just_attacked = True
                self.paralyze()
                self.target_kitty.just_been_hit = True

    @property
    def should_sprint(self):
        return self.in_range or self.target_kitty is not None

    def draw_debug(self):
        just_been_hit_text = arcade.Text(f"Just been hit: {self.just_been_hit}", self.center_x, self.center_y+50, arcade.color.WHITE, 12)
        just_been_hit_text.draw()
