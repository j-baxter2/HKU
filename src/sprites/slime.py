import arcade
from pyglet.math import Vec2
import math
from src.data.constants import M, DELTA_TIME, SOUND_EFFECT_VOL
from src.utils.sound import play_sound

class Slime(arcade.Sprite):
    def __init__(self, scene: arcade.Scene = None, filename: str = None, scale: float = 1, image_x: float = 0, image_y: float = 0, image_width: float = 0, image_height: float = 0, center_x: float = 0, center_y: float = 0, repeat_count_x: int = 1, repeat_count_y: int = 1, flipped_horizontally: bool = False, flipped_vertically: bool = False, flipped_diagonally: bool = False, hit_box_algorithm: str = "Simple", hit_box_detail: float = 4.5, texture: arcade.Texture = None, angle: float = 0):
        super().__init__(filename, scale, image_x, image_y, image_width, image_height, center_x, center_y, repeat_count_x, repeat_count_y, flipped_horizontally, flipped_vertically, flipped_diagonally, hit_box_algorithm, hit_box_detail, texture, angle)
        self.scene = scene
        self.player = self.scene.get_sprite_list("Player")[0]
        self.timer = 0
        self.lifetime = 5

        self.affecting = False
        self.effect_timer = 0
        self.effect_time = 3

    def update(self, delta_time=DELTA_TIME):
        self.player = self.scene.get_sprite_list("Player")[0]
        self.timer += DELTA_TIME
        if not self.affecting:
            if arcade.check_for_collision(self, self.player):
                self.affecting = True
            if self.timer >= self.lifetime:
                self.rescale_relative_to_point(point=[self.center_x, self.center_y], factor=0.8)
                if self.height < 2:
                    self.kill()
        else:
            self.effect_timer += DELTA_TIME
            component = min(max(0,255*(self.effect_timer/self.effect_time)),255)
            self.player.color = [255,255,component]
            self.player.velocity = Vec2(self.player.velocity[0], self.player.velocity[1])
            self.player.velocity = self.player.velocity.scale(0.3)
            if self.effect_timer >= self.effect_time:
                self.affecting = False
                self.player.color = arcade.color.WHITE
                self.effect_timer = 0
