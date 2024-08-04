import arcade
import math
from pyglet.math import Vec2
import time
from src.sprites.living_sprite import LivingSprite
from src.sprites.projectile_specify import ProjectileSpecify
from src.moves.move_by_player import MoveByPlayer
import json
from src.data.constants import DELTA_TIME, SOUND_EFFECT_VOL, LINE_HEIGHT
from src.utils.sound import load_sound, play_sound

class MoveMouseAim(MoveByPlayer):
    def __init__(self, id: int, scene: arcade.Scene, origin_sprite: LivingSprite):
        super().__init__(id, scene, origin_sprite)
        self.sub_active_timer = 0
        self.projectiles_fired = 0
        self.n_projectiles = 20
        self.window = arcade.get_window()
        self.fire_sound = load_sound("explosion2")

    def get_values_from_mouse(self):
        start = self.origin_sprite.position
        target = self.window.views["game"].mouse_pos
        origin_to_mouse = Vec2(target[0]-start[0],target[1]-start[1])
        origin_to_mouse = origin_to_mouse.normalize()
        distance = arcade.get_distance(*start, *target)
        origin_to_mouse = origin_to_mouse.scale(min(distance, self.range))
        target = (start[0] + origin_to_mouse[0], start[1] + origin_to_mouse[1])
        range=origin_to_mouse.mag
        return start, target, range

    def start(self):
        self.active = True
        self.active_timer = 0
        self.sub_active_timer = 0
        self.projectiles_fired = 0

    def fire_projectile(self):
        start, target, proj_range = self.get_values_from_mouse()
        self.projectile = ProjectileSpecify(0, self.scene, self, start=start, target=target, targetting_method="tuple", range=proj_range)
        self.scene.add_sprite("Projectile", self.projectile)
        self.projectile.start()

    def update_activity(self):
        if self.active:
            self.active_timer += DELTA_TIME
            self.sub_active_timer += DELTA_TIME
            self.update_activity_mobility()
            self.origin_sprite.color = self.color
            if self.sub_active_timer >= self.active_time / self.n_projectiles:
                self.fire_projectile()
                play_sound(self.fire_sound)
                self.projectiles_fired+=1
                self.sub_active_timer=0
            if self.active_timer > self.active_time:
                self.stop()

    def execute(self):
        if self.executable:
            self.start()

    def draw(self):
        if self.active:
            _, target, _  = self.get_values_from_mouse()
            arcade.draw_circle_outline(center_x=target[0], center_y=target[1], radius=32, color=self.color[:3])
            arcade.draw_circle_filled(center_x=target[0], center_y=target[1], radius=32, color=self.color[:3]+(128,))
