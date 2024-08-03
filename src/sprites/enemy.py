import arcade
from src.sprites.following_sprite import FollowingSprite
from src.sprites.player import Player
from pyglet.math import Vec2
import random
import math
import json
from src.data.constants import MAP_WIDTH, MAP_HEIGHT, DELTA_TIME

class BaseEnemy(FollowingSprite):
    def __init__(self, id : int, scene: arcade.Scene):
        with open("resources/data/enemy.json", "r") as file:
            enemy_dict = json.load(file)
        self.enemy_data = enemy_dict[str(id)]
        super().__init__(self.enemy_data, self.scene)
        self.max_hp = self.enemy_data["hp"]
        self.hp = self.max_hp

    def setup(self):
        super().setup()

    def update_while_alive(self):
        pass

    @property
    def in_range(self):
        return arcade.get_distance_between_sprites(self, self.player) < self.follow_distance

    @property
    def should_sprint(self):
        return self.in_range

    def draw_debug(self):
        just_been_hit_text = arcade.Text(f"Just been hit: {self.just_been_hit}", self.center_x, self.center_y+50, arcade.color.WHITE, 12)
        just_been_hit_text.draw()
