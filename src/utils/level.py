import json
import arcade
from src.sprites.enemy import FollowingEnemy
from src.sprites.player import Player
from src.sprites.kitty import Kitty
from src.data.constants import MAP_WIDTH, MAP_HEIGHT

class Level:
    def __init__(self, level_id, player: Player, game_section):
        self.level_id = level_id
        self.player = player
        self.game_section = game_section
        self.enemy_data = self.load_level_data(level_id)["enemies"]
        self.enemies = arcade.SpriteList()
        self.kitty_data = self.load_level_data(level_id)["kitties"]
        self.kitties = arcade.SpriteList()
        self.treats = self.game_section.treat_sprite_list

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
                enemy = FollowingEnemy(id=int(enemy_id), player=self.player)
                enemy.position = arcade.rand_in_rect([0,0], map_bounds[0], map_bounds[1])
                self.enemies.append(enemy)

    def load_kitties(self):
        kitty_amount = self.kitty_data["kitty amount"]
        kitty_ratio = self.kitty_data["kitty ratio"]
        map_bounds = [MAP_WIDTH, MAP_HEIGHT]

        for kitty_id, ratio in kitty_ratio.items():
            for _ in range(int(ratio * kitty_amount)):
                kitty = Kitty(id=int(kitty_id), treats=self.treats)
                kitty.position = arcade.rand_in_rect([0,0], map_bounds[0], map_bounds[1])
                self.kitties.append(kitty)

    def spawn_player(self):
        self.player.center_x, self.player.center_y = 300, 300

    def get_level_list(self):
        return self.level_list
