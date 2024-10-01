import arcade
from pyglet.math import Vec2
import math
from data.constants import M, DELTA_TIME, SOUND_EFFECT_VOL
from sprites.following_sprite import FollowingSprite
from utils.sound import load_sound, play_sound

class Slime(arcade.Sprite):
    def __init__(self, scene: arcade.Scene = None, finite: bool = False, filename: str = None, scale: float = 1, image_x: float = 0, image_y: float = 0, image_width: float = 0, image_height: float = 0, center_x: float = 0, center_y: float = 0, repeat_count_x: int = 1, repeat_count_y: int = 1, flipped_horizontally: bool = False, flipped_vertically: bool = False, flipped_diagonally: bool = False, hit_box_algorithm: str = "Simple", hit_box_detail: float = 4.5, texture: arcade.Texture = None, angle: float = 0):
        super().__init__(filename, scale, image_x, image_y, image_width, image_height, center_x, center_y, repeat_count_x, repeat_count_y, flipped_horizontally, flipped_vertically, flipped_diagonally, hit_box_algorithm, hit_box_detail, texture, angle)
        self.scene = scene
        self.player = self.scene.get_sprite_list("Player")[0]
        self.finite = finite
        self.timer = 0
        self.lifetime = 5 if finite else None
        self.shrinking = False

        self.affecting = False
        self.effect_timer = 0
        self.effect_time = 3

        self.squelch = load_sound("squelch", source="hku")
        self.shrink = load_sound("fall3")

    def update(self, delta_time=DELTA_TIME):
        if len(self.scene.get_sprite_list("Player")) > 0:
            self.player = self.scene.get_sprite_list("Player")[0]
        self.timer += DELTA_TIME
        if not self.affecting:
            if arcade.check_for_collision(self, self.player):
                self.affecting = True
                play_sound(self.squelch, volume=SOUND_EFFECT_VOL*(arcade.get_window().sfx_vol))
                self.finite = True
                self.timer = 0
                self.lifetime = 1
        else:
            self.effect_timer += DELTA_TIME
            component = int(min(max(0,255*(self.effect_timer/self.effect_time)),255))
            self.player.color = [255,255,component]
            self.player.speed_multiplier = 0.3
            if self.effect_timer >= self.effect_time:
                self.affecting = False
                self.player.color = arcade.color.WHITE
                self.player.speed_multiplier = 1
                self.effect_timer = 0
        if self.finite:
                if self.timer >= self.lifetime:
                    if not self.shrinking:
                        play_sound(self.shrink, volume=self.get_volume_from_player_pos(), pan=self.get_pan_from_player_pos())
                    self.rescale_relative_to_point(point=[self.center_x, self.center_y], factor=0.8)
                    self.shrinking = True
                    if self.height < 2 and not self.affecting:
                        self.kill()

    def get_volume_from_player_pos(self):
        distance = arcade.get_distance_between_sprites(self, self.player)
        distance_in_m = distance / M
        if distance == 0:
            volume = 1
        else:
            volume = 1/(distance_in_m)
        return min(max(volume, 0)*SOUND_EFFECT_VOL*(arcade.get_window().sfx_vol), 1)

    def get_pan_from_player_pos(self):
        angle = arcade.get_angle_radians(self.player.center_x, self.player.center_y, self.center_x, self.center_y)
        return math.sin(angle)
