import arcade
import math
from src.sprites.living_sprite import LivingSprite
import json
from src.data.constants import DELTA_TIME, SOUND_EFFECT_VOL, LINE_HEIGHT
from src.utils.sound import load_sound, play_sound

class Move:
    def __init__(self, id: int, scene: arcade.Scene, origin_sprite: LivingSprite):
        with open("resources/data/move.json", "r") as file:
            moves_dict = json.load(file)
        self.move_data = moves_dict[str(id)]

        self.scene = scene
        self.origin_sprite = origin_sprite

        self.name = self.move_data["name"]
        self.type = self.move_data["type"]
        self.damage = self.move_data["damage"]
        self.active_time = self.move_data["active time"]
        self.refresh_time = self.move_data["refresh time"]
        self.range = self.move_data["range"]
        self.origin_mobile_while_charging = self.move_data["origin mobile while charging"]
        self.origin_mobile_while_active = self.move_data["origin mobile while active"]
        self.affectees_mobile_while_active = self.move_data["affectees mobile while active"]
        self.affects = self.move_data["affects"]
        self.charge_time = self.move_data["charge time"]
        self.color_key = self.move_data["color"]
        self.draw_lines = self.move_data["draw lines"]
        self.draw_circle = self.move_data["draw circle"]
        self.start_sound_name = self.move_data["start sound"]
        self.stop_sound_name = self.move_data["stop sound"]

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
        self.update_affectees()
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
        self.get_affectees()
        play_sound(self.start_sound, volume=SOUND_EFFECT_VOL)

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
        self.stop_activity_mobility()
        play_sound(self.stop_sound, volume=SOUND_EFFECT_VOL)
        self.origin_sprite.color = arcade.color.WHITE
        self.active_timer = 0

    def execute(self):
        if self.executable:
            self.start()
            self.apply_effects()

    def get_affectees(self):
        pass

    def update_affectees(self):
        for affectee in self.affectees:
            if affectee.is_dead:
                self.affectees.remove(affectee)

    def apply_effects(self):
        for affectee in self.affectees:
            if self.damage < 0:
                affectee.take_damage(self.damage)
                affectee.just_healed = True
            elif self.damage >= 0:
                affectee.take_damage(self.damage)

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

    def draw_debug(self, index: int):
        start_x = self.origin_sprite.center_x+self.origin_sprite.width
        start_y = self.origin_sprite.top-index*(LINE_HEIGHT*4)
        active_debug_text = arcade.Text(f"{self.name} active: {self.active}\nactiveprogress: {round(self.progress_fraction, 2)}", start_x=start_x, start_y=start_y, color=arcade.color.BLACK, font_size=12, width=self.origin_sprite.width, anchor_x="left", anchor_y="top", multiline=True)
        active_debug_text.draw()
        if self.refreshing:
            refresh_debug_text = arcade.Text(f"refreshing: {self.refreshing}\nrefreshprogress: {round(self.refresh_fraction, 2)}", start_x=start_x+self.origin_sprite.width, start_y=start_y, color=arcade.color.BLACK, font_size=12, width=self.origin_sprite.width, anchor_x="left", anchor_y="top", multiline=True)
            refresh_debug_text.draw()
        if self.charging:
            charging_debug_text = arcade.Text(f"charging: {self.charging}\nchargeprogress: {round(self.charge_fraction, 1)}", start_x=start_x+self.origin_sprite.width*2, start_y=start_y, color=arcade.color.BLACK, font_size=12, width=self.origin_sprite.width, anchor_x="left", anchor_y="top", multiline=True)
            charging_debug_text.draw()

    @property
    def executable(self):
        return not self.active and not (self.origin_sprite.fading or self.origin_sprite.faded) and self.charged and not self.refreshing

    @property
    def refresh_fraction(self):
        return self.refresh_timer / self.refresh_time

    @property
    def progress_fraction(self):
        return self.active_timer / self.active_time

    @property
    def charge_fraction(self):
        return self.charge_timer / self.charge_time
