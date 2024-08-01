import arcade
import math
from src.sprites.living_sprite import LivingSprite
from src.sprites.projectile import Projectile
from src.moves.move import Move
import json
from src.data.constants import DELTA_TIME, SOUND_EFFECT_VOL, LINE_HEIGHT
from src.utils.sound import load_sound, play_sound

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
                affectee.start_just_been_hit()
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
                affectee.start_just_been_hit()

    @property
    def executable(self):
        return super().executable and self.origin_sprite.stamina >= self.cost
