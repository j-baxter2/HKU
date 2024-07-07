import json
import arcade
import numpy as np
from src.sprites.kitty import FollowingKitty
from src.sprites.player import Player

class Level:
    def __init__(self, level_id, player: Player, game_section):
        self.level_id = level_id
        self.player = player
        self.game_section = game_section
        self.kitty_data = self.load_level_data(level_id)["kitties"]
        self.kitties = arcade.SpriteList()

    def load_level_data(self, level_id):
        with open("resources/data/level.json", "r") as file:
            level_data = json.load(file)
        return level_data[str(level_id)]

    def load_kitties(self):
        kitty_amount = self.kitty_data["kitty amount"]
        kitty_ratio = self.kitty_data["kitty ratio"]
        map_bounds = self.game_section.map_bounds

        for kitty_id, ratio in kitty_ratio.items():
            for _ in range(int(ratio * kitty_amount)):
                kitty = FollowingKitty(id=int(kitty_id), player=self.player)
                kitty.center_x = np.random.uniform(0, map_bounds[0])
                kitty.center_y = np.random.uniform(0, map_bounds[1])
                self.kitties.append(kitty)
