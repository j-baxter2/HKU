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

        self.enemy_amount = self.enemy_data["enemy amount"]
        self.enemy_ratio = self.enemy_data["enemy ratio"]

        self.kitty_amount = self.kitty_data["kitty amount"]
        self.kitty_ratio = self.kitty_data["kitty ratio"]

        self.treat_amount = 0

        self.initial_enemy_count = {enemy_id: int(ratio * self.enemy_amount) for enemy_id, ratio in self.enemy_ratio.items()}


    def load_level_data(self, level_id):
        with open("resources/data/level.json", "r") as file:
            level_data = json.load(file)
        self.level_list = [int(level) for level in level_data.keys()]
        return level_data[str(level_id)]

    def load_enemies(self):
        map_bounds = [MAP_WIDTH, MAP_HEIGHT]

        for enemy_id, ratio in self.enemy_ratio.items():
            for _ in range(int(ratio * self.enemy_amount)):
                self.spawn_enemy(enemy_id=enemy_id, map_bounds=map_bounds)

    def spawn_enemy(self, enemy_id, map_bounds):
        if enemy_id == "0":
            enemy = DistruptorEnemy(id=int(enemy_id), scene=self.scene)
        elif enemy_id == "2":
            enemy = ShootingEnemy(id=int(enemy_id), scene=self.scene)

        while True:
            x = random.uniform(0, map_bounds[0])
            y = random.uniform(0, map_bounds[1])
            if not (0 <= x <= 1024 and 0 <= y <= 1024):
                break
        enemy.position = (x, y)
        self.scene.add_sprite("Enemy", enemy)
        enemy.setup()

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

    def get_level_list(self):
        return self.level_list

    def update_respawn_enemies(self):
        map_bounds = [MAP_WIDTH, MAP_HEIGHT]
        current_enemy_counts = {"0": 0, "1": 0, "2": 0}

        # Count current enemies
        for enemy in self.scene.get_sprite_list("Enemy"):
            if isinstance(enemy, DistruptorEnemy):
                current_enemy_counts["0"] += 1
                current_enemy_counts["1"] += 1
            elif isinstance(enemy, ShootingEnemy):
                current_enemy_counts["2"] += 1

        for enemy_id, initial_count in self.initial_enemy_count.items():
            threshold = 0.7 * initial_count
            if current_enemy_counts[enemy_id] < threshold:
                # Calculate how many enemies to respawn
                respawn_count = int(threshold) - current_enemy_counts[enemy_id]
                for _ in range(respawn_count):
                    self.spawn_enemy(enemy_id, map_bounds)

    def spawn_treats(self):
        for kitty in self.scene.get_sprite_list("Kitty"):
            self.treat_amount += kitty.hunger
        edge_margin = 64  # Avoid spawning too close to the edge

        for i in range(self.treat_amount):
            x = random.uniform(edge_margin, MAP_WIDTH - edge_margin)
            y = random.uniform(edge_margin, MAP_HEIGHT - edge_margin)

            # Create and place the treat
            treat = Treat("resources/spritesheets/treat.png", 4, decayed=True)
            treat.position = (x, y)
            self.scene.add_sprite("Treat", treat)
