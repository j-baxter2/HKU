import arcade
from sprites.following_sprite import FollowingSprite
from sprites.player import Player
from pyglet.math import Vec2
import random
import math
import json
from data.constants import MAP_WIDTH, MAP_HEIGHT, DELTA_TIME
from utils.sound import load_sound, play_sound

class BaseEnemy(FollowingSprite):
    def __init__(self, id : int, scene: arcade.Scene):
        with open("resources/data/enemy.json", "r") as file:
            enemy_dict = json.load(file)
        self.enemy_data = enemy_dict[str(id)]
        super().__init__(self.enemy_data, self.scene)
        self.max_hp = self.enemy_data["hp"]
        self.fade_texture_index = self.enemy_data["spritesheet"]["fade texture"]
        self.hp = self.max_hp
        self.death_sound = load_sound("gobu_scream", source="hku")
        self.attack_sounds = [load_sound("gobu_attack01", source="hku"), load_sound("gobu_attack02", source="hku")]

    def setup(self):
        super().setup()

    def update_while_alive(self):
        pass

    def start_fade(self):
        play_sound(self.death_sound, volume=self.get_volume_from_player_pos(), pan=self.get_pan_from_player_pos())
        super().start_fade()

    @property
    def in_range(self):
        return arcade.get_distance_between_sprites(self, self.player) < self.follow_distance and not self.player.inside

    @property
    def should_sprint(self):
        return self.in_range

    def draw_debug(self):
        just_been_hit_text = arcade.Text(f"Just been hit: {self.just_been_hit}", self.center_x, self.center_y+50, arcade.color.WHITE, 12)
        just_been_hit_text.draw()
