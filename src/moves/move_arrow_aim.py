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

class MoveArrowAim(MoveByPlayer):
    def __init__(self, id: int, scene: arcade.Scene, origin_sprite: LivingSprite):
        super().__init__(id, scene, origin_sprite)
        self.sub_active_timer = 0
        self.projectiles_fired = 0
        self.n_projectiles = 20
        self.window = arcade.get_window()
        self.fire_sound = load_sound("explosion2")
        self.choosing_target = False
        self.origin_sprite = origin_sprite
        self.target = origin_sprite.position

    def start(self):
        self.active = True
        self.active_timer = 0
        self.sub_active_timer = 0
        self.projectiles_fired = 0
        self.target = (self.origin_sprite.left, self.origin_sprite.top)

    def fire_projectile(self):
        start = self.origin_sprite.position
        target = self.target
        origin_to_target = Vec2(target[0]-start[0],target[1]-start[1])
        origin_to_target = origin_to_target.normalize()
        distance = arcade.get_distance(*start, *target)
        origin_to_target = origin_to_target.scale(min(distance, self.range))
        target = (start[0] + origin_to_target[0], start[1] + origin_to_target[1])
        proj_range=origin_to_target.mag
        self.projectile = ProjectileSpecify(0, self.scene, self, start=start, target=self.target, targetting_method="tuple", range=proj_range)

        self.scene.add_sprite("Projectile", self.projectile)
        self.projectile.start()

    def update_activity(self):
        if self.active:
            self.choosing_target = True
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
                self.choosing_target = False

    def execute(self):
        if self.executable:
            self.start()

    def change_target(self, direction: str):
        if self.choosing_target:
            if direction == "up" and self.target:
                self.target = (self.target[0],self.target[1]+32)
            elif direction == "down" and self.target:
                self.target = (self.target[0],self.target[1]-32)
            elif direction == "left" and self.target:
                self.target = (self.target[0]-32,self.target[1])
            elif direction == "right" and self.target:
                self.target = (self.target[0]+32,self.target[1])

    def draw(self):
        if self.active:
            arcade.draw_circle_outline(center_x=self.target[0], center_y=self.target[1], radius=32, color=self.color[:3])
            arcade.draw_circle_filled(center_x=self.target[0], center_y=self.target[1], radius=32, color=self.color[:3]+(128,))
