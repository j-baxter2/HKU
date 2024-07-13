import arcade
from src.sprites.moving_sprite import MovingSprite
import json

class Move:
    def __init__(self, id: int, scene: arcade.Scene, origin_sprite: MovingSprite):
        with open("resources/data/move.json", "r") as file:
            moves_dict = json.load(file)
        move_data = moves_dict[str(id)]

        self.scene = scene
        self.origin_sprite = origin_sprite

        self.name = move_data["name"]
        self.damage = move_data["damage"]
        self.cost = move_data["cost"]
        self.active_time = move_data["active time"]
        self.range = move_data["range"]
        self.affects = move_data["affects"]
        self.color_key = move_data["color"]

        self.active = False
        self.active_for = 0

        self.color = getattr(arcade.color, self.color_key.upper())


    def start(self):
        self.active = True
        self.active_for = 0
        self.origin_sprite.stamina -= self.cost
        self.origin_sprite.color = self.color

    def on_update(self, delta_time: float):
        if self.active:
            self.active_for += delta_time
            if self.active_for > self.active_time:
                self.stop()

    def stop(self):
        self.active = False
        self.origin_sprite.color = arcade.color.WHITE
        self.active_for = 0

    def execute(self):
        if self.executable:
            self.start()
            self.damage_affectees()

    def get_affectees(self):
        affectees = []
        potential_affectees = self.scene.get_sprite_list(self.affects)
        for potential_affectee in potential_affectees:
            if arcade.get_distance_between_sprites(self.origin_sprite, potential_affectee) < self.range:
                affectees.append(potential_affectee)
        return affectees

    def damage_affectees(self):
        affectees = self.get_affectees()
        for affectee in affectees:
            affectee.take_damage(self.damage)
            affectee.just_been_hit = True

    def draw(self):
        arcade.draw_circle_outline(self.origin_sprite.center_x, self.origin_sprite.center_y, self.range, [255,0,255,32], 5)

        arcade.draw_circle_outline(self.origin_sprite.center_x, self.origin_sprite.center_y, self.range*max(0.5, self.progress_fraction), [255, 0, 0, 255*(self.progress_fraction)], 5)

        for affectee in self.get_affectees():
            arcade.draw_line(self.origin_sprite.center_x, self.origin_sprite.center_y, affectee.center_x, affectee.center_y, arcade.color.RED, 5)

    def debug_draw(self):
        arcade.draw_text(f"{self.name}: {self.active}\n{round(self.active_for, 1)}/{self.active_time}", self.origin_sprite.center_x - 50, self.origin_sprite.center_y - 100, arcade.color.BLACK, 12)

    @property
    def executable(self):
        return not self.active

    @property
    def progress_fraction(self):
        return self.active_for / self.active_time
