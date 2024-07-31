import arcade
import math
from src.sprites.living_sprite import LivingSprite
from src.sprites.projectile import Projectile
from src.moves.move_by_player import MoveByPlayer
import json
from src.data.constants import DELTA_TIME, SOUND_EFFECT_VOL, LINE_HEIGHT
from src.utils.sound import load_sound, play_sound

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
