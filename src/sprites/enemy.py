import arcade
from src.sprites.following_sprite import FollowingSprite
from src.sprites.player import Player
from pyglet.math import Vec2
import random
import math
import json
from src.data.constants import MAP_WIDTH, MAP_HEIGHT, DELTA_TIME

class FollowingEnemy(FollowingSprite):
    def __init__(self, id : int, player : Player):
        with open("resources/data/enemy.json", "r") as file:
            enemy_dict = json.load(file)
        self.enemy_data = enemy_dict[str(id)]

        self.player = player

        self.max_hp = self.enemy_data["hp"]
        self.hp = self.max_hp
        self.attack = self.enemy_data["attack"]

        self.follow_distance = self.enemy_data["follow radius"]
        self.follow_speed_bonus = self.enemy_data["follow speed bonus"]

        self.change_direction_time = self.enemy_data["change direction time"]
        self.random_movement_timer = 0

        self.velocity = Vec2(0, 0)

        self.just_attacked = False
        self.attack_refresh_time = 0

        self.fading = False
        self.fade_timer = 0
        self.fade_time = 1

        super().__init__(self.enemy_data, self.player)
