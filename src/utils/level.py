import json
import math
import arcade
import random
from src.sprites.distruptor_enemy import DistruptorEnemy
from src.sprites.shooting_enemy import ShootingEnemy
from src.sprites.player import Player
from src.sprites.treat import Treat
from src.sprites.kitty import Kitty
from src.data.constants import MAP_WIDTH, MAP_HEIGHT

class Level:
    def __init__(self, level_id, scene: arcade.Scene):
        self.level_id = level_id
        self.scene = scene
        self.player = self.scene.get_sprite_list("Player")[0]
        self.enemy_data = self.load_level_data(level_id)["enemies"]
        self.kitty_data = self.load_level_data(level_id)["kitties"]
        self.treats = self.scene.get_sprite_list("Treat")

        self.kitty_amount = self.kitty_data["kitty amount"]
        self.kitty_ratio = self.kitty_data["kitty ratio"]

        self.treat_amount = 0

    def load_level_data(self, level_id):
        with open("resources/data/level.json", "r") as file:
            level_data = json.load(file)
        self.level_list = [int(level) for level in level_data.keys()]
        return level_data[str(level_id)]

    def load_enemies(self):
        enemy_amount = self.enemy_data["enemy amount"]
        enemy_ratio = self.enemy_data["enemy ratio"]
        map_bounds = [MAP_WIDTH, MAP_HEIGHT]

        for enemy_id, ratio in enemy_ratio.items():
            for _ in range(int(ratio * enemy_amount)):
                if enemy_id == "0":
                    enemy = DistruptorEnemy(id=int(enemy_id), scene=self.scene)
                elif enemy_id == "2":
                    enemy = ShootingEnemy(id=int(enemy_id), scene=self.scene)
                while True:
                    x = random.uniform(0, map_bounds[0])
                    y = random.uniform(0, map_bounds[1])
                    if not (0 <= x <= 1024 and 0 <= y <= 1024):
                        break
                enemy.position = (x,y)
                self.scene.add_sprite("Enemy", enemy)

    def load_kitties(self):
        map_bounds = [MAP_WIDTH, MAP_HEIGHT]

        for kitty_id, ratio in self.kitty_ratio.items():
            for _ in range(int(ratio * self.kitty_amount)):
                kitty = Kitty(id=int(kitty_id), scene=self.scene)
                while True:
                    x = random.uniform(0, map_bounds[0])
                    y = random.uniform(0, map_bounds[1])
                    if not (0 <= x <= 1024 and 0 <= y <= 1024):
                        break
                kitty.position = (x,y)
                self.scene.add_sprite("Kitty", kitty)

    def spawn_player(self):
        self.player.center_x, self.player.center_y = 300, 300

    def get_level_list(self):
        return self.level_list

    def spawn_treats(self):
        for kitty in self.scene.get_sprite_list("Kitty"):
            self.treat_amount += kitty.hunger
        edge_margin = 64  # Avoid spawning too close to the edge

        for i in range(self.treat_amount):
            x = random.uniform(edge_margin, MAP_WIDTH - edge_margin)
            y = random.uniform(edge_margin, MAP_HEIGHT - edge_margin)

            # Create and place the treat
            treat = Treat("resources/textures/map_tiles/default_apple.png", 0.8, decayed=True)
            treat.position = (x, y)
            self.scene.add_sprite("Treat", treat)
