import arcade
from src.data.constants import DELTA_TIME, SOUND_EFFECT_VOL

def load_sound(name:str, source = "builtin", file_type = "wav"):
    if source == "builtin":
        path = f":resources:sounds/{name}.{file_type}"
    elif source == "hku":
        path = f"resources/sounds/{name}.{file_type}"
    else:
        path = name

    if name != None:
        sound = arcade.load_sound(path)
        return sound
    else:
        pass

def play_sound(sound, volume = 1.0, pan = 0.0, speed = 1.0, looping = False, return_player = False):
    if sound:
        player = arcade.play_sound(sound, volume=volume, pan=pan, speed=speed, looping=looping)
        if return_player:
            return player
    else:
        pass

class FootstepSoundHandler:
    def __init__(self, origin_sprite: arcade.Sprite):
        self.origin_sprite = origin_sprite

        self.sound_update_timer = 0
        self.swung_8th_notes_multipliers = [4/7, 3/7]
        self.current_multiplier_index = 0

    def update_sound(self):
        self.update_walking_sound()

    def update_walking_sound(self):
        if self.origin_sprite.stationary:
            self.sound_update_timer = 0
        else:
            self.sound_update_timer += DELTA_TIME

        if self.sound_update_timer >= self.sound_update_time * self.swung_8th_notes_multipliers[self.current_multiplier_index]:
            play_sound(self.origin_sprite.footstep_sounds[self.origin_sprite.cur_footstep_key], volume=SOUND_EFFECT_VOL*0.5)
            self.sound_update_timer = 0
            self.current_multiplier_index = (self.current_multiplier_index + 1) % len(self.swung_8th_notes_multipliers)

    @property
    def sound_update_time(self):
        return 0.3 / (1+int(self.origin_sprite.should_sprint)) / self.origin_sprite.speed_multiplier
