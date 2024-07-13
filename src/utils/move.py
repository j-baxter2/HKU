import arcade
from src.sprites.moving_sprite import MovingSprite
import json
from src.data.constants import DELTA_TIME

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
        self.refresh_time = move_data["refresh time"]
        self.range = move_data["range"]
        self.affects = move_data["affects"]
        self.charge_time = move_data["charge time"]
        self.color_key = move_data["color"]
        self.draw_lines = move_data["draw lines"]
        self.draw_circle = move_data["draw circle"]

        self.active = False
        self.active_timer = 0

        self.refreshing = False
        self.refresh_timer = 0

        self.charging = False
        self.charge_timer = 0
        self.charged = True if self.charge_time==0 else False

        self.color = getattr(arcade.color, self.color_key.upper())

    def on_update(self, delta_time: float):
        self.update_activity()
        self.update_charge()
        self.update_refresh()

    def start_refresh(self):
        self.refreshing = True
        self.refresh_timer = 0

    def update_refresh(self):
        if self.refreshing:
            self.refresh_timer += DELTA_TIME
            if self.refresh_timer > self.refresh_time:
                self.refreshing = False
                self.refresh_timer = 0

    def start_charge(self):
        self.charging = True
        self.charge_timer = 0

    def update_charge(self):
        if self.charging:
            self.charge_timer += DELTA_TIME
            if self.charge_timer > self.charge_time:
                self.stop_charge()
                self.charged = True
                self.execute()

    def stop_charge(self):
        self.charging = False
        self.charge_timer = 0

    def start(self):
        self.active = True
        self.active_timer = 0
        self.origin_sprite.stamina -= self.cost
        self.origin_sprite.color = self.color

    def update_activity(self):
        if self.active:
            self.active_timer += DELTA_TIME
            if self.active_timer > self.active_time:
                self.stop()

    def stop(self):
        self.active = False
        self.refreshing = True
        self.charged = True if self.charge_time==0 else False
        self.origin_sprite.color = arcade.color.WHITE
        self.active_timer = 0

    def execute(self):
        if self.executable:
            self.start()
            self.damage_affectees()

    def get_affectees(self):
        affectees = []
        potential_affectees = self.scene.get_sprite_list(self.affects)
        for potential_affectee in potential_affectees:
            if self.origin_sprite == potential_affectee:
                affectees.append(potential_affectee)
            elif arcade.get_distance_between_sprites(self.origin_sprite, potential_affectee) < self.range:
                affectees.append(potential_affectee)
        return affectees

    def damage_affectees(self):
        affectees = self.get_affectees()
        for affectee in affectees:
            affectee.take_damage(self.damage)
            if self.damage < 0:
                affectee.just_healed = True
            elif self.damage > 0:
                affectee.just_been_hit = True

    def draw(self):
        if self.draw_circle:
            arcade.draw_circle_outline(self.origin_sprite.center_x, self.origin_sprite.center_y, self.range, [255,0,255,32], 5)

            arcade.draw_circle_outline(self.origin_sprite.center_x, self.origin_sprite.center_y, self.range*max(0.5, self.progress_fraction), [255, 0, 0, 255*(self.progress_fraction)], 5)

        if self.draw_lines:
            for affectee in self.get_affectees():
                arcade.draw_line(self.origin_sprite.center_x, self.origin_sprite.center_y, affectee.center_x, affectee.center_y, arcade.color.RED, 5)

    def debug_draw(self):
        arcade.draw_text(f"{self.name}: {self.active}\n{round(self.active_timer, 1)}/{self.active_time}", self.origin_sprite.center_x - 50, self.origin_sprite.center_y - 100, arcade.color.BLACK, 12)
        if self.charging:
            arcade.draw_text(f"Charging {self.name}: {round(self.charge_fraction, 1)}", self.origin_sprite.center_x - 50, self.origin_sprite.center_y - 150, arcade.color.BLACK, 12)

    @property
    def executable(self):
        return not self.active and self.origin_sprite.stamina >= self.cost and not (self.origin_sprite.fading or self.origin_sprite.faded) and self.charged and not self.refreshing

    @property
    def refresh_fraction(self):
        return self.refresh_timer / self.refresh_time

    @property
    def progress_fraction(self):
        return self.active_timer / self.active_time

    @property
    def charge_fraction(self):
        return self.charge_timer / self.charge_time
