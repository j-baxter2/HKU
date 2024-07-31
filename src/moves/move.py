import arcade
import math
from src.sprites.living_sprite import LivingSprite
from src.sprites.projectile import Projectile
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
                affectee.just_been_hit = True

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

class MoveByPlayer(Move):
    def __init__(self, id: int, scene: arcade.Scene, origin_sprite: LivingSprite):
        super().__init__(id, scene, origin_sprite)
        self.slot = self.move_data["slot"]
        self.damage_resist = self.move_data["damage resist"]
        self.cost = self.move_data["cost"]
        self.origin_sprite.all_moves.append(self)

    def start(self):
        super().start()
        self.start_damage_resist()
        self.origin_sprite.stamina -= self.cost

    def stop(self):
        super().stop()
        self.stop_damage_resist()

    def apply_effects(self):
        for affectee in self.affectees:
            if self.damage < 0:
                affectee.take_damage(self.damage)
                affectee.just_healed = True
            elif self.damage >= 0:
                affectee.take_damage(self.damage * self.origin_sprite.strength)
                affectee.just_been_hit = True
                if affectee.is_dead:
                    self.origin_sprite.give_xp(affectee.max_hp * affectee.attack)

    def start_damage_resist(self):
        if self.damage_resist:
            self.origin_sprite.damage_resist += self.damage_resist

    def stop_damage_resist(self):
        if self.damage_resist:
            if self.origin_sprite.damage_resist > 0:
                self.origin_sprite.damage_resist -= self.damage_resist
            else:
                self.origin_sprite.damage_resist = 0

    def apply_effects(self):
        for affectee in self.affectees:
            if self.damage < 0:
                affectee.take_damage(self.damage)
                affectee.just_healed = True
            elif self.damage >= 0:
                affectee.take_damage(self.damage)
                affectee.just_been_hit = True

    @property
    def executable(self):
        return super().executable and self.origin_sprite.stamina >= self.cost

class TargetArrowKey(MoveByPlayer):
    def __init__(self, id: int, scene: arcade.Scene, origin_sprite: LivingSprite):
        super().__init__(id, scene, origin_sprite)
        self.choosing_target = False
        self.choosing_target_timer = 0
        self.target = None
        self.potential_target = None
        self.origin_pos_when_fired = None
        self.target_pos_when_fired = None
        self.projectile = None

    def on_update(self, delta_time: float):
        self.update_activity()
        self.update_charge()
        self.update_choose_target()
        self.update_refresh()

    def start_charge(self):
        if self.able_to_start_charge:
            self.charging = True
            self.start_choose_target()

    def update_charge(self):
        if self.charging:
            self.charge_timer += DELTA_TIME
            if self.charge_timer >= self.charge_time:
                self.stop_charge(success=True)

    def stop_charge(self, success: bool = False):
        self.charging = False
        if success:
            self.charged = True
            self.charge_timer = self.charge_time
        else:
            self.charged = False
            self.charge_timer = 0
            self.stop_choose_target()
            if self.target is not None:
                self.target.color = arcade.color.WHITE

    def start(self):
        self.active = True
        self.active_timer = 0
        play_sound(self.start_sound, volume=SOUND_EFFECT_VOL)
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
        self.hit_sprites = None
        self.stop_damage_resist()
        self.stop_activity_mobility()
        play_sound(self.stop_sound, volume=SOUND_EFFECT_VOL)
        self.origin_sprite.color = arcade.color.WHITE
        self.target = None
        self.active_timer = 0

    def fire(self):
        if self.target is not None and self.executable:
            self.start()
            self.stop_choose_target()
            self.set_origin_pos_when_fired()
            self.set_target_pos_when_fired()
            angle = arcade.get_angle_degrees(*self.origin_pos_when_fired, *self.target_pos_when_fired)
            self.projectile = Projectile(0, self.scene, self, start=self.origin_pos_when_fired, angle=angle, targetting_method="angle")
            self.scene.add_sprite("Projectile", self.projectile)
            self.projectile.start()
            self.charge_timer = 0
        else:
            self.stop_charge(success=False)

    def set_origin_pos_when_fired(self):
        self.origin_pos_when_fired = (self.origin_sprite.center_x, self.origin_sprite.center_y)

    def set_target_pos_when_fired(self):
        self.target_pos_when_fired = (self.target.center_x, self.target.center_y)

    def start_choose_target(self):
        self.choosing_target = True
        potential_targets = self.scene.get_sprite_list(self.affects)
        for potential_target in potential_targets:
            if arcade.get_distance_between_sprites(self.origin_sprite, potential_target) < self.range and not (potential_target.fading or potential_target.faded):
                self.target = potential_target
                break

    def change_target(self, direction: str):
        if self.choosing_target:
            potential_targets = self.scene.get_sprite_list(self.affects)
            if direction == "any":
                potential_any_targets = [target for target in potential_targets if target != self.target]
                self.potential_target = arcade.get_closest_sprite(self.origin_sprite, potential_any_targets)[0]
            elif direction == "up" and self.target:
                potential_up_targets = [target for target in potential_targets if target.center_y > self.target.center_y]
                self.potential_target = arcade.get_closest_sprite(self.origin_sprite, potential_up_targets)[0]
            elif direction == "down" and self.target:
                potential_down_targets = [target for target in potential_targets if target.center_y < self.target.center_y]
                self.potential_target = arcade.get_closest_sprite(self.origin_sprite, potential_down_targets)[0]
            elif direction == "left" and self.target:
                potential_left_targets = [target for target in potential_targets if target.center_x < self.target.center_x]
                self.potential_target = arcade.get_closest_sprite(self.origin_sprite, potential_left_targets)[0]
            elif direction == "right" and self.target:
                potential_right_targets = [target for target in potential_targets if target.center_x > self.target.center_x]
                self.potential_target = arcade.get_closest_sprite(self.origin_sprite, potential_right_targets)[0]
            if self.potential_target_in_range:
                self.old_target = self.target
                self.old_target.color = arcade.color.WHITE
                self.target = self.potential_target

    def update_choose_target(self):
        if self.choosing_target:
            self.choosing_target_timer += DELTA_TIME
            if self.target is not None:
                self.target.color = self.color

    def stop_choose_target(self):
        self.choosing_target = False
        if self.target is not None:
            self.target.color = arcade.color.WHITE
        self.choosing_target_timer = 0

    def draw(self):
        if self.choosing_target:
            if self.target is not None:
                arcade.draw_line(self.origin_sprite.center_x, self.origin_sprite.center_y, self.target.center_x, self.target.center_y, self.color[:3]+(max(0,min(128*math.sin(self.charge_fraction*self.choosing_target_timer*100)+128,255)),), 5)

    @property
    def able_to_start_charge(self):
        return not self.active and not self.charging and not self.charged and not self.refreshing and not (self.origin_sprite.fading or self.origin_sprite.faded)

    @property
    def potential_target_in_range(self):
        return self.potential_target is not None and arcade.get_distance_between_sprites(self.origin_sprite, self.potential_target) < self.range

    def draw_debug(self, index: int):
        super().draw_debug(index)
        start_x = self.origin_sprite.center_x+self.origin_sprite.width
        start_y = self.origin_sprite.top-index*(LINE_HEIGHT*4)
        if self.choosing_target:
            charging_debug_text = arcade.Text(f"choosing: {self.choosing_target}\ntarget: {self.target is not None}", start_x=start_x+self.origin_sprite.width, start_y=start_y, color=arcade.color.BLACK, font_size=12, width=self.origin_sprite.width, anchor_x="left", anchor_y="top", multiline=True)
            charging_debug_text.draw()

class RadialProjectile(MoveByPlayer):
    def __init__(self, id: int, scene: arcade.Scene, origin_sprite: LivingSprite):
        super().__init__(id, scene, origin_sprite)
        self.projectile = None

    def apply_effects(self):
        origin_pos_when_fired = self.origin_sprite.position
        for i in range(8):
            self.projectile = Projectile(0, self.scene, self, start=origin_pos_when_fired, angle=45*i, targetting_method="angle")
            self.scene.add_sprite("Projectile", self.projectile)
            self.projectile.start()

    def draw(self):
        if self.charging:
            for i in range(8):
                x = self.origin_sprite.center_x + math.sin(math.radians(45*i))*self.range
                y = self.origin_sprite.center_y + math.cos(math.radians(45*i))*self.range
                arcade.draw_circle_outline(center_x=x, center_y=y, radius=32, color=self.color[:3])
                arcade.draw_circle_filled(center_x=x, center_y=y, radius=32, color=self.color[:3]+(128,))

class AffectAllMove(MoveByPlayer):
    def __init__(self, id: int, scene: arcade.Scene, origin_sprite: LivingSprite):
        super().__init__(id, scene, origin_sprite)

    def get_affectees(self):
        affectees = []
        potential_affectees = self.scene.get_sprite_list(self.affects)
        for potential_affectee in potential_affectees:
            if self.origin_sprite == potential_affectee:
                affectees.append(potential_affectee)
            elif arcade.get_distance_between_sprites(self.origin_sprite, potential_affectee) < self.range and not (potential_affectee.fading or potential_affectee.faded):
                affectees.append(potential_affectee)
        self.affectees = affectees
