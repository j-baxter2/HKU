import arcade
from src.sprites.moving_sprite import MovingSprite
import json

class Player(MovingSprite):
    def __init__(self, id: int):
        # Load player data from JSON
        with open("resources/data/player.json", "r") as file:
            player_dict = json.load(file)
        self.player_data = player_dict[str(id)]

        super().__init__(self.player_data)

        self.sprint_multiplier = self.player_data["sprint multiplier"]

        self.cuteness = 0
        self.score = 0

    def take_damage(self, damage):
        self.cuteness += damage

    def increase_score(self, points):
        self.score += points
