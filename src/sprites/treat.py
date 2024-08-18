import arcade
from src.data.constants import DELTA_TIME
import math

class Treat(arcade.Sprite):
    def __init__(self, image_file, scale=1, decayed=False):
        super().__init__(image_file, scale)
        self.being_eaten = False
        self.picked_up = False

        self.healthy = True
        self.life_timer = 0
        self.healthy_time = 0.5
        self.decaying = False
        self.decayed = decayed
        self.decay_timer = 0
        self.decay_time = 1
        self.opacity_timer = 0

    def update(self):
        self.bob()
        self.life_timer += DELTA_TIME
        if self.healthy:
            if self.life_timer >= self.healthy_time:
                self.healthy = False
                self.decaying = True
        if self.decaying:
            self.decay_timer += DELTA_TIME
            if self.decay_timer >= self.decay_time:
                self.decayed = True
                self.decaying = False
                self.decay_timer = 0
        if self.decayed:
            self.opacity_timer += DELTA_TIME
        self.update_appearance()

    def update_appearance(self):
        self.visible = not self.being_eaten
        if self.decayed:
            self.color = arcade.color.GRANNY_SMITH_APPLE[:3]+(max(0,min(64*math.sin(self.opacity_timer*10)+192,255)),)
        else:
            self.color = arcade.color.WHITE

    def bob(self):
        self.center_y += math.sin(self.life_timer*4)*0.5

    def draw_debug(self):
        decay_text = arcade.Text(f"Decaying: {self.decaying} {round(self.decay_fraction*100,2)}%\n Decayed: {self.decayed}\n Healthy: {self.healthy}\n Lifetime: {round(self.life_timer,1)}s", start_x=self.center_x, start_y=self.top, color=arcade.color.BLACK, font_size=12, anchor_x="center", anchor_y="bottom", multiline=True, width = 256)
        decay_text.draw()

    @property
    def decay_fraction(self):
        return self.decay_timer / self.decay_time

    @property
    def healthy_fraction(self):
        return self.life_timer / self.healthy_time

    @property
    def edible(self):
        return not self.decayed and not self.being_eaten
