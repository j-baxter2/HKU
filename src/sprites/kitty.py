import arcade
from src.sprites.moving_sprite import MovingSprite
import json

class FollowingKitty(MovingSprite):
    def __init__(self, id : int, player : arcade.Sprite):
        # Load player data from JSON
        with open("resources/data/kitty.json", "r") as file:
            kitty_dict = json.load(file)
        self.kitty_data = kitty_dict[str(id)]

        self.player = player
        self.follow_distance = self.kitty_data["follow radius"]
        super().__init__(self.kitty_data)

    def update(self):
        # Calculate the distance to the player
        distance_to_player = arcade.get_distance_between_sprites(self, self.player)

        # If the kitty is further away from the player than the follow distance, move towards the player
        if distance_to_player > self.follow_distance:
            self.center_x += (self.player.center_x - self.center_x) * 0.05
            self.center_y += (self.player.center_y - self.center_y) * 0.05

        super().update()
