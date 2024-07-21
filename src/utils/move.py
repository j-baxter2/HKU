import arcade
from src.sprites.moving_sprite import MovingSprite
import json
from src.data.constants import DELTA_TIME
from src.utils.sound import load_sound, play_sound

class Move:
    def __init__(self, id: int, scene: arcade.Scene, origin_sprite: MovingSprite):
        with open("resources/data/move.json", "r") as file:
            moves_dict = json.load(file)
        move_data = moves_dict[str(id)]

        self.scene = scene
        self.origin_sprite = origin_sprite

        self.name = move_data["name"]
        self.damage = move_data["damage"]
        self.damage_resist = move_data["damage resist"]
        self.cost = move_data["cost"]
        self.active_time = move_data["active time"]
        self.refresh_time = move_data["refresh time"]
        self.range = move_data["range"]
        self.origin_mobile_while_charging = move_data["origin mobile while charging"]
        self.origin_mobile_while_active = move_data["origin mobile while active"]
        self.affectees_mobile_while_active = move_data["affectees mobile while active"]
        self.affects = move_data["affects"]
        self.charge_time = move_data["charge time"]
        self.color_key = move_data["color"]
        self.draw_lines = move_data["draw lines"]
        self.draw_circle = move_data["draw circle"]
        self.start_sound_name = move_data["start sound"]
        self.stop_sound_name = move_data["stop sound"]

        self.affectees = []

        self.active = False
        self.active_timer = 0

        self.refreshing = False
        self.refresh_timer = 0

        self.charging = False
        self.charge_timer = 0
        self.charged = False if self.charge_time else True

        self.color = getattr(arcade.color, self.color_key.upper())


        self.start_sound = load_sound(self.start_sound_name)

        self.stop_sound = load_sound(self.stop_sound_name)

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
            self.update_charge_mobility()
            if self.charge_timer > self.charge_time:
                self.stop_charge()
                self.charged = True
                self.execute()

    def stop_charge(self):
        self.charging = False
        self.charge_timer = 0
        self.stop_charge_mobility()

    def start(self):
        self.active = True
        self.active_timer = 0
        self.start_damage_resist()
        play_sound(self.start_sound)
        self.origin_sprite.stamina -= self.cost

    def update_activity(self):
        if self.active:
            self.active_timer += DELTA_TIME
            self.update_activity_mobility()
            self.origin_sprite.color = self.color
            if self.active_timer > self.active_time:
                self.stop()

    def stop(self):
        self.active = False
        self.refreshing = True
        self.charged = False if self.charge_time else True
        self.stop_damage_resist()
        self.stop_activity_mobility()
        play_sound(self.stop_sound)
        self.origin_sprite.color = arcade.color.WHITE
        self.active_timer = 0

    def execute(self):
        if self.executable:
            self.start()
            self.apply_effects()

    def get_affectees(self):
        affectees = []
        potential_affectees = self.scene.get_sprite_list(self.affects)
        for potential_affectee in potential_affectees:
            if self.origin_sprite == potential_affectee:
                affectees.append(potential_affectee)
            elif arcade.get_distance_between_sprites(self.origin_sprite, potential_affectee) < self.range:
                affectees.append(potential_affectee)
        self.affectees = affectees

    def apply_effects(self):
        for affectee in self.affectees:
            affectee.take_damage(self.damage)
            if self.damage < 0:
                affectee.just_healed = True
            elif self.damage > 0:
                affectee.just_been_hit = True

    def start_damage_resist(self):
        if self.damage_resist:
            self.origin_sprite.damage_resist += self.damage_resist

    def stop_damage_resist(self):
        if self.damage_resist:
            if self.origin_sprite.damage_resist > 0:
                self.origin_sprite.damage_resist -= self.damage_resist
            else:
                self.origin_sprite.damage_resist = 0

    def update_activity_mobility(self):
        if not self.origin_mobile_while_active:
            self.origin_sprite.paralyze()
        if not self.affectees_mobile_while_active:
            for affectee in self.affectees:
                affectee.paralyze()

    def stop_activity_mobility(self):
        if not self.origin_mobile_while_active:
            self.origin_sprite.start_moving()
        if not self.affectees_mobile_while_active:
            for affectee in self.affectees:
                affectee.start_moving()

    def update_charge_mobility(self):
        if not self.origin_mobile_while_charging:
            self.origin_sprite.paralyze()

    def stop_charge_mobility(self):
        if not self.origin_mobile_while_charging:
            self.origin_sprite.start_moving()

    def draw(self):
        if self.draw_circle:
            constant_opacity_color = self.color[:3] + (32,)
            arcade.draw_circle_outline(self.origin_sprite.center_x, self.origin_sprite.center_y, self.range, constant_opacity_color, 5)

            variable_opacity = int(255 * self.progress_fraction)
            variable_opacity_color = self.color[:3] + (variable_opacity,)
            arcade.draw_circle_outline(self.origin_sprite.center_x, self.origin_sprite.center_y, self.range * max(0.5, self.progress_fraction), variable_opacity_color, 5)

        if self.draw_lines:
            for affectee in self.affectees:
                arcade.draw_line(self.origin_sprite.center_x, self.origin_sprite.center_y, affectee.center_x, affectee.center_y, self.color, 5)

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
