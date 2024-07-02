import arcade
from src.sprites.moving_sprite import MovingSprite
import json
from pyglet.math import Vec2

class Player(MovingSprite):
    def __init__(self, id: int):
        # Load player data from JSON
        with open("resources/data/player.json", "r") as file:
            player_dict = json.load(file)
        self.player_data = player_dict[str(id)]

        # Initialise the MovingSprite class
        super().__init__(self.player_data)

        # Load movement data from JSON
        self.sprint_multiplier = self.player_data["sprint multiplier"]
        self.max_stamina = self.player_data["stamina"]
        self.stamina_regen = self.player_data["stamina regen"]
        self.stamina_regen_bonus_stationary = self.player_data["stationary stamina bonus"]

        # Set up player variables
        self.cuteness = 0
        self.score = 0
        self.stamina = self.max_stamina
        self.sprinting = False

    def update_stamina(self, delta_time):
        # Subtract stamina when sprinting
        if self.sprinting:
            self.stamina -= 1
        # Regenerate quicker when stationary
        elif self.speed == 0:
            self.stamina += (self.stamina_regen + self.stamina_regen_bonus_stationary) * delta_time
        # Normal regeneration when walking
        else:
            self.stamina += self.stamina_regen * delta_time

        # Ensure stamina does not exceed max stamina or drop below 0
        self.stamina = max(0, min(self.stamina, self.max_stamina))

    def take_damage(self, damage):
        self.cuteness += damage

    def increase_score(self, points):
        self.score += points
