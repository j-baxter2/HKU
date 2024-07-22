import arcade
from src.sprites.following_sprite import FollowingSprite
from src.sprites.player import Player
from pyglet.math import Vec2
import random
import math
import json
from src.data.constants import MAP_WIDTH, MAP_HEIGHT, DELTA_TIME

class FollowingEnemy(FollowingSprite):
    def __init__(self, id : int, player : Player, kitties: arcade.SpriteList):
        with open("resources/data/enemy.json", "r") as file:
            enemy_dict = json.load(file)
        self.enemy_data = enemy_dict[str(id)]

        self.player = player
        self.kitties = kitties

        self.max_hp = self.enemy_data["hp"]
        self.hp = self.max_hp
        self.attack = self.enemy_data["attack"]

        self.just_attacked = False
        self.attack_refresh_time = 0

        self.target_kitty = None

        super().__init__(self.enemy_data, self.player)

    def update(self):
        if self.fading:
            self.update_fade()
        else:
            if self.able_to_move:
                self.update_movement()
            self.random_movement_timer += DELTA_TIME
            self.update_animation(delta_time = DELTA_TIME)
            self.look_for_eating_kitty()
            if self.target_kitty:
                self.update_target_kitty()
                self.handle_kitty_collision()
            self.handle_player_collision()
            self.update_attack_refresh()
            super().update()

    def update_attack_refresh(self):
        if self.just_attacked:
            self.attack_refresh_time += DELTA_TIME
            if self.attack_refresh_time >= 1:
                self.reset_attack_timer()

    def reset_attack_timer(self):
        self.just_attacked = False
        self.attack_refresh_time = 0

    def update_movement(self):
        super().update_movement()

    def update_movement_direction(self):
        if self.target_kitty:
            self.face_kitty()
        elif self.in_range and not self.player.faded:
            self.face_player()
        elif self.should_turn:
            self.randomize_velocity()
            self.random_movement_timer = 0

    def update_movement_speed(self):
        if self.in_range or self.target_kitty:
            self.speed = self.follow_speed_bonus * self.base_speed
        else:
            self.speed = self.base_speed

    def face_kitty(self):
        self.velocity = Vec2(self.target_kitty.center_x - self.center_x, self.target_kitty.center_y - self.center_y)

    def look_for_eating_kitty(self):
        for kitty in self.kitties:
            if arcade.get_distance_between_sprites(self, kitty) < self.follow_distance and kitty.eating:
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
                self.target_kitty.just_been_hit = True
