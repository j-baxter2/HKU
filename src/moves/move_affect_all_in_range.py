import arcade
import math
from src.sprites.living_sprite import LivingSprite
from src.sprites.projectile import Projectile
from src.moves.move_by_player import MoveByPlayer
import json
from src.data.constants import DELTA_TIME, SOUND_EFFECT_VOL, LINE_HEIGHT
from src.utils.sound import load_sound, play_sound

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
