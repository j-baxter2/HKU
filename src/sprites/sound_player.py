import arcade
import math
from src.data.constants import M, DELTA_TIME, SOUND_EFFECT_VOL
from src.utils.sound import play_sound

class AmbientPlayer(arcade.Sprite):
    def __init__(self, scene: arcade.Scene = None, filename: str = None, scale: float = 1, image_x: float = 0, image_y: float = 0, image_width: float = 0, image_height: float = 0, center_x: float = 0, center_y: float = 0, sound: arcade.Sound = None, repeat_count_x: int = 1, repeat_count_y: int = 1, flipped_horizontally: bool = False, flipped_vertically: bool = False, flipped_diagonally: bool = False, hit_box_algorithm: str = "Simple", hit_box_detail: float = 4.5, texture: arcade.Texture = None, angle: float = 0):
        super().__init__(filename, scale, image_x, image_y, image_width, image_height, center_x, center_y, repeat_count_x, repeat_count_y, flipped_horizontally, flipped_vertically, flipped_diagonally, hit_box_algorithm, hit_box_detail, texture, angle)
        self.sound = sound
        self.scene = scene
        self.player = self.scene.get_sprite_list("Player")[0]
        self.timer = 0

    def update(self, delta_time=DELTA_TIME):
        self.player = self.scene.get_sprite_list("Player")[0]
        self.timer += DELTA_TIME
        if self.timer >= self.sound.get_length():
            self.play()
            self.timer = 0

    def play(self):
        play_sound(self.sound, volume=self.get_volume_from_player_pos()*SOUND_EFFECT_VOL, pan=self.get_pan_from_player_pos())

    def get_volume_from_player_pos(self):
        distance = arcade.get_distance_between_sprites(self, self.player)
        distance_in_m = distance / M
        if distance == 0:
            volume = 1
        else:
            volume = 5/(distance_in_m)
        return min(max(volume, 0), 1)

    def get_pan_from_player_pos(self):
        angle = arcade.get_angle_radians(self.player.center_x, self.player.center_y, self.center_x, self.center_y)
        return math.sin(angle)
