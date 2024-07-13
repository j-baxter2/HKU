import arcade
from src.sprites.moving_sprite import MovingSprite
import json
from pyglet.math import Vec2
from src.utils.move import Move
from src.data.constants import DELTA_TIME

class Player(MovingSprite):

    def __init__(self, id: int):
        # Load player data from JSON
        with open("resources/data/player.json", "r") as file:
            player_dict = json.load(file)
        self.player_data = player_dict[str(id)]

        # Initialise the MovingSprite class
        super().__init__(self.player_data)

        self.name = self.player_data["name"]

        # Load movement data from JSON
        self.sprint_multiplier = self.player_data["sprint multiplier"]
        self.max_stamina = self.player_data["stamina"]
        self.stamina_regen = self.player_data["stamina regen"]
        self.stamina_regen_bonus_stationary = self.player_data["stationary stamina bonus"]

        # Initialise moveset
        self.move_set = []

        # Set up player variables
        self.hp = self.max_hp
        self.score = 0
        self.stamina = self.max_stamina
        self.sprinting = False

        self.fading = False
        self.fade_timer = 0
        self.fade_time = 1

    def setup(self):
        super().setup()

    def update(self):
        super().update()

    def draw(self):
        super().draw()

    def update_stamina(self, delta_time):
        # Subtract stamina when sprinting
        if self.sprinting:
            self.stamina -= 1
        # Regenerate quicker when stationary
        elif self.stationary:
            self.stamina += (self.stamina_regen + self.stamina_regen_bonus_stationary) * delta_time
        # Normal regeneration when walking
        else:
            self.stamina += self.stamina_regen * delta_time

        # Ensure stamina does not exceed max stamina or drop below 0
        self.stamina = max(0, min(self.stamina, self.max_stamina))

    def update_fade(self):
        self.fade_timer += DELTA_TIME
        opacity_decrease = 255 * (self.fade_timer / 2)
        self.alpha = max(255 - opacity_decrease, 0)
        if self.fade_timer >= self.fade_time:
            self.fading = False
            self.faded = True
            self.kill()

    def increase_score(self, points):
        self.score += points

    def get_integer_position(self):
        return (int(self.center_x), int(self.center_y))

    def add_move(self, move):
        self.move_set.append(move)

    def do_move(self, move_name: str):
        for move in self.move_set:
            if move.name == move_name and move.executable and self.stamina >= move.cost and not (self.fading or self.faded):
                move.execute()

    def debug_draw(self):
        self.draw_hit_box()
        for move in self.move_set:
            move.debug_draw()
        arcade.draw_text(f"JBH: {self.just_been_hit}", self.center_x, self.center_y+100, arcade.color.WHITE, 20)
        super().debug_draw()

    @property
    def doing_move(self):
        for move in self.move_set:
            if move.active:
                return True
        return False

    def get_active_move(self):
        for move in self.move_set:
            if move.active:
                return move
        return None
