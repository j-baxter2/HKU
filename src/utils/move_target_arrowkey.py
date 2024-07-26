import arcade
import math
from src.utils.move import Move
from src.sprites.living_sprite import LivingSprite
from src.utils.sound import play_sound
from src.data.constants import DELTA_TIME, SOUND_EFFECT_VOL, LINE_HEIGHT

class TargetArrowKey(Move):
    def __init__(self, id: int, scene: arcade.Scene, origin_sprite: LivingSprite):
        super().__init__(id, scene, origin_sprite)
        self.choosing_target = False
        self.choosing_target_timer = 0
        self.target = None
        self.potential_target = None
        self.origin_pos_when_fired = None
        self.target_pos_when_fired = None
        self.projectile = arcade.Sprite()
        self.hit_sprites = None

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
            self.get_hit_sprites()
            if self.hit_sprites is not None:
                for sprite in self.hit_sprites:
                    self.damage_sprite(sprite)
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

    def damage_sprite(self, sprite):
        sprite.take_damage(self.damage)
        if sprite.is_dead:
            self.origin_sprite.give_xp(sprite.max_hp*sprite.attack)

    def fire(self):
        if self.target is not None and self.executable:
            self.start()
            self.stop_choose_target()
            self.set_origin_pos_when_fired()
            self.set_target_pos_when_fired()
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
        if self.active:
            bullet_x = self.origin_pos_when_fired[0] + (self.target_pos_when_fired[0] - self.origin_pos_when_fired[0]) * self.progress_fraction
            bullet_y = self.origin_pos_when_fired[1] + (self.target_pos_when_fired[1] - self.origin_pos_when_fired[1]) * self.progress_fraction
            self.projectile = arcade.Sprite("resources/textures/map_tiles/default_obsidian_shard.png")
            self.projectile.center_x = bullet_x
            self.projectile.center_y = bullet_y
            self.projectile.draw()

    @property
    def executable(self):
        return not self.active and self.origin_sprite.stamina >= self.cost and not (self.origin_sprite.fading or self.origin_sprite.faded) and self.charged and not self.refreshing and self.charged

    @property
    def able_to_start_charge(self):
        return not self.active and not self.charging and not self.charged and not self.refreshing and not (self.origin_sprite.fading or self.origin_sprite.faded)

    @property
    def potential_target_in_range(self):
        return self.potential_target is not None and arcade.get_distance_between_sprites(self.origin_sprite, self.potential_target) < self.range

    def get_hit_sprites(self):
        potential_hit_sprites = self.scene.get_sprite_list(self.affects)
        self.hit_sprites = arcade.check_for_collision_with_list(self.projectile, potential_hit_sprites)

    def draw_debug(self, index: int):
        super().draw_debug(index)
        start_x = self.origin_sprite.center_x+self.origin_sprite.width
        start_y = self.origin_sprite.top-index*(LINE_HEIGHT*4)
        if self.choosing_target:
            charging_debug_text = arcade.Text(f"choosing: {self.choosing_target}\ntarget: {self.target is not None}", start_x=start_x+self.origin_sprite.width, start_y=start_y, color=arcade.color.BLACK, font_size=12, width=self.origin_sprite.width, anchor_x="left", anchor_y="top", multiline=True)
            charging_debug_text.draw()
