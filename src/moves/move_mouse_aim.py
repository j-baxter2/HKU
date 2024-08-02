import arcade
import math
import time
from src.sprites.living_sprite import LivingSprite
from src.sprites.projectile import Projectile
from src.moves.move_by_player import MoveByPlayer
import json
from src.data.constants import DELTA_TIME, SOUND_EFFECT_VOL, LINE_HEIGHT
from src.utils.sound import load_sound, play_sound

class MoveMouseAim(MoveByPlayer):
    def __init__(self, id: int, scene: arcade.Scene, origin_sprite: LivingSprite):
        super().__init__(id, scene, origin_sprite)
        self.sub_active_timer = 0
        self.projectiles_fired = 0
        self.n_projectiles = 25
        self.window = arcade.get_window()

    def start(self):
        self.active = True
        self.active_timer = 0
        self.sub_active_timer = 0
        self.projectiles_fired = 0

    def fire_projectile(self):
        start = self.origin_sprite.position
        target = self.window.views["game"].mouse_pos
        print(f"{target}")
        self.projectile = Projectile(0, self.scene, self, start=start, target=target, targetting_method="tuple")
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
                self.projectiles_fired+=1
                self.sub_active_timer=0
            if self.active_timer > self.active_time:
                self.stop()

    def execute(self):
        if self.executable:
            self.start()
