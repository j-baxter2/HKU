import arcade
from data.constants import DELTA_TIME, SOUND_EFFECT_VOL
from utils.sound import play_sound, load_sound
import math


class Bench(arcade.Sprite):
    def __init__(self, scene, center_x, center_y, filename, scale):
        super().__init__(center_x=center_x, center_y=center_y, filename=filename, scale=scale)
        self.scene = scene
        self.player = self.scene.get_sprite_list("Player")[0]
        self.music_player = None
        self.sound = load_sound("jump3")
        self.timer = 0
        self.time = self.sound.get_length()

    def update(self, delta_time: float = 1/60):
        if len(self.scene.get_sprite_list("Player")) > 0:
            self.player = self.scene.get_sprite_list("Player")[0]
        self.timer += DELTA_TIME
        if self.music_player is not None:
            self.music_player.volume = self.get_volume_from_player_pos() if self.player.has_never_equipped_move else 0
            self.music_player.pan = self.get_pan_from_player_pos()
        self.color = [255, 0.5 * math.sin(self.timer * 0.1 * math.pi / self.time)*127 + 127, 255, 255] if self.player.has_never_equipped_move else [255, 255, 255, 255]
        if self.timer >= self.time:
            self.play()
            self.timer = 0

    def play(self):
        self.music_player = play_sound(self.sound, volume=self.get_volume_from_player_pos() if self.player.has_never_equipped_move else 0, pan=self.get_pan_from_player_pos(), return_player=True)

    def get_volume_from_player_pos(self):
        distance = arcade.get_distance_between_sprites(self, self.player)
        if distance == 0:
            volume = 0.5
        elif distance < 1024:
            volume = (1024-distance)/1024 * 0.5
        elif distance >= 1024:
            volume = 0
        return min(max(volume, 0)*SOUND_EFFECT_VOL*(arcade.get_window().sfx_vol), 1)

    def get_pan_from_player_pos(self):
        angle = arcade.get_angle_radians(self.player.center_x, self.player.center_y, self.center_x, self.center_y)
        return math.sin(angle)
