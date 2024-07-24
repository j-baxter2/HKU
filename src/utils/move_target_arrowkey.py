import arcade
from src.utils.move import Move
from src.sprites.moving_sprite import MovingSprite
from src.utils.sound import play_sound
from src.data.constants import DELTA_TIME, SOUND_EFFECT_VOL

class TargetArrowKey(Move):
    def __init__(self, id: int, scene: arcade.Scene, origin_sprite: MovingSprite):
        super().__init__(id, scene, origin_sprite)
        self.choosing_target = False
        self.target_chosen = False

    def on_update(self, delta_time: float):
        self.update_affectees()
        self.update_activity()
        self.update_charge()
        self.update_refresh()

    def start_charge(self):
        self.charging = True
        self.charge_timer = 0

    def update_charge(self):
        if self.charging:
            self.charge_timer += DELTA_TIME
            self.update_charge_mobility()
            if self.charge_timer > self.charge_time:
                self.start_choosing_target()

    def stop_charge(self):
        self.charging = False
        self.charge_timer = 0
        self.stop_charge_mobility()

    def start(self):
        self.active = True
        self.active_timer = 0
        self.get_affectees()
        self.start_damage_resist()
        play_sound(self.start_sound, volume=SOUND_EFFECT_VOL)
        self.origin_sprite.stamina -= self.cost

    def execute(self):
        if self.executable:
            self.start()
            self.apply_effects()

    def get_affectees(self):
        affectees = []
        potential_affectees = self.scene.get_sprite_list(self.affects)
        for potential_affectee in potential_affectees:
            if self.origin_sprite == potential_affectee:
                affectees.append(potential_affectee)
            elif arcade.get_distance_between_sprites(self.origin_sprite, potential_affectee) < self.range and not (potential_affectee.fading or potential_affectee.faded):
                affectees.append(potential_affectee)
        self.affectees = affectees

    def apply_effects(self):
        for affectee in self.affectees:
            if self.damage < 0:
                affectee.take_damage(self.damage)
                affectee.just_healed = True
            elif self.damage > 0:
                affectee.take_damage(self.damage * self.origin_sprite.strength)
                affectee.just_been_hit = True
                if affectee.is_dead:
                    self.origin_sprite.give_xp(affectee.max_hp * affectee.attack)

    @property
    def executable(self):
        return not self.active and self.origin_sprite.stamina >= self.cost and not (self.origin_sprite.fading or self.origin_sprite.faded) and self.charged and not self.refreshing
