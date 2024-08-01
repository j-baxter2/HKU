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

    def update_movement_direction(self):
        if self.should_turn:
            self.randomize_velocity()
            self.random_movement_timer = 0

    def face_player(self):
        apparent_player_position = self.apparent_player_position()
        self.velocity = Vec2(apparent_player_position[0] - self.center_x, apparent_player_position[1] - self.center_y)

    def apparent_player_position(self, vision=0.0):
        true_player_position = self.player.position
        distance = arcade.get_distance_between_sprites(self, self.player)
        apparent_player_position = (true_player_position[0] + random.uniform(-distance*(1-vision), distance*(1-vision)), true_player_position[1] + random.uniform(-distance*(1-vision), distance*(1-vision)))
        return apparent_player_position

    @property
    def in_range(self):
        return arcade.get_distance_between_sprites(self, self.player) < self.follow_distance

    @property
    def should_sprint(self):
        return self.in_range

    def draw_debug(self):
        just_been_hit_text = arcade.Text(f"Just been hit: {self.just_been_hit}", self.center_x, self.center_y+50, arcade.color.WHITE, 12)
        just_been_hit_text.draw()
