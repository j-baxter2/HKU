import arcade
import math
from src.sprites.living_sprite import LivingSprite
from src.sprites.projectile import Projectile
from src.moves.move import Move
import json
from src.data.constants import DELTA_TIME, SOUND_EFFECT_VOL, LINE_HEIGHT
from src.utils.sound import load_sound, play_sound

class MoveEnemyShoot(Move):
    def __init__(self, id: int, scene: arcade.Scene, origin_sprite: LivingSprite):
        super().__init__(id, scene, origin_sprite)
