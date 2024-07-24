import arcade
from src.utils.move import Move
from src.sprites.moving_sprite import MovingSprite
from src.utils.sound import play_sound
from src.data.constants import DELTA_TIME, SOUND_EFFECT_VOL, LINE_HEIGHT

class TargetArrowKey(Move):
    def __init__(self, id: int, scene: arcade.Scene, origin_sprite: MovingSprite):
        super().__init__(id, scene, origin_sprite)
        self.type = self.move_data["type"]
        self.choosing_target = False
        self.target = None
        self.potential_target = None

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

    def fire(self):
        if self.target is not None and self.executable:
            self.start()
            self.stop_choose_target()
            arcade.draw_line(self.origin_sprite.center_x, self.origin_sprite.center_y, self.target.center_x, self.target.center_y, self.color, 5)
            self.target.take_damage(self.damage)
            if self.target.is_dead:
                self.origin_sprite.give_xp(self.target.max_hp*self.target.attack)
            self.charge_timer = 0
        else:
            self.stop_charge(success=False)

    def start_choose_target(self):
        self.choosing_target = True
        potential_targets = self.scene.get_sprite_list(self.affects)
        for potential_target in potential_targets:
            if arcade.get_distance_between_sprites(self.origin_sprite, potential_target) < self.range and (not potential_target.fading or potential_target.faded):
                self.target = potential_target
                break

    def change_target(self, direction: str):
        print("change target executed")
        if self.choosing_target:
            potential_targets = self.scene.get_sprite_list(self.affects)
            if direction == "up" and self.target:
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
            if self.target is not None:
                self.target.color = self.color
                arcade.draw_line(self.origin_sprite.center_x, self.origin_sprite.center_y, self.target.center_x, self.target.center_y, self.color, 5)

    def draw(self):
        if self.choosing_target:
            if self.target is not None:
                arcade.draw_line(self.origin_sprite.center_x, self.origin_sprite.center_y, self.target.center_x, self.target.center_y, self.color, 5)

    def stop_choose_target(self):
        self.choosing_target = False

    @property
    def executable(self):
        return not self.active and self.origin_sprite.stamina >= self.cost and not (self.origin_sprite.fading or self.origin_sprite.faded) and self.charged and not self.refreshing and self.charged

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
