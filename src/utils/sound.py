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

def play_sound(sound, volume = 1.0, pan = 0.0, speed = 1.0):
    if sound:
        arcade.play_sound(sound, volume=volume, pan=pan, speed=speed)
    else:
        pass

class FootstepSoundHandler:
    def __init__(self, sound: arcade.Sound, origin_sprite: arcade.Sprite):
        self.footstep_sound = sound
        self.origin_sprite = origin_sprite

        self.sound_update_timer = 0# Base time for sound updates
        self.swung_8th_notes_multipliers = [4/7, 3/7]
        self.current_multiplier_index = 0  # Index to track which multiplier to use
        self.stationary = False

    def update_sound(self):
        self.update_walking_sound()

    def update_walking_sound(self):
        if self.origin_sprite.stationary:
            self.sound_update_timer = 0
        else:
            self.sound_update_timer += DELTA_TIME

        if self.sound_update_timer >= self.sound_update_time * self.swung_8th_notes_multipliers[self.current_multiplier_index]:
            play_sound(self.footstep_sound, volume=SOUND_EFFECT_VOL)
            self.sound_update_timer = 0
            # Switch to the next multiplier for the swung rhythm
            self.current_multiplier_index = (self.current_multiplier_index + 1) % len(self.swung_8th_notes_multipliers)

    @property
    def sound_update_time(self):
        return 0.3 / (1+int(self.origin_sprite.should_sprint))
