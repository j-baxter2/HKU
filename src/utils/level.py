import json
import arcade
from src.sprites.enemy import FollowingEnemy
from src.sprites.player import Player
from src.data.constants import MAP_WIDTH, MAP_HEIGHT

class Level:
    def __init__(self, level_id, player: Player, game_section):
        self.level_id = level_id
        self.player = player
        self.game_section = game_section
        self.enemy_data = self.load_level_data(level_id)["enemies"]
        self.enemies = arcade.SpriteList()

    def load_level_data(self, level_id):
        with open("resources/data/level.json", "r") as file:
            level_data = json.load(file)
        return level_data[str(level_id)]

    def load_enemies(self):
        enemy_amount = self.enemy_data["enemy amount"]
        enemy_ratio = self.enemy_data["enemy ratio"]
        map_bounds = [MAP_WIDTH, MAP_HEIGHT]

        for enemy_id, ratio in enemy_ratio.items():
            for _ in range(int(ratio * enemy_amount)):
                enemy = FollowingEnemy(id=int(enemy_id), player=self.player)
                enemy.position = arcade.rand_in_rect([0,0], map_bounds[0], map_bounds[1])
                self.enemies.append(enemy)

    def spawn_player(self):
        self.player.center_x, self.player.center_y = 300, 300
