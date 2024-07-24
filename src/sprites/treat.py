import arcade
from src.data.constants import DELTA_TIME

class Treat(arcade.Sprite):
    def __init__(self, image_file, scale=1):
        super().__init__(image_file, scale)
        self.being_eaten = False
        self.picked_up = False

        self.healthy = True
        self.healthy_timer = 0
        self.healthy_time = 1
        self.decaying = False
        self.decayed = False
        self.decay_timer = 0
        self.decay_time = 2

    def update(self):
        if self.healthy:
            self.healthy_timer += DELTA_TIME
            if self.healthy_timer >= self.healthy_time:
                self.healthy = False
                self.decaying = True
                self.healthy_timer = 0
        if self.decaying:
            self.decay_timer += DELTA_TIME
            if self.decay_timer >= self.decay_time:
                self.decayed = True
                self.decaying = False
                self.decay_timer = 0
        self.update_color()

    def update_color(self):
        if self.decayed:
            self.color = arcade.color.GRAY
        else:
            self.color = arcade.color.WHITE

    def draw_debug(self):
        decay_text = arcade.Text(f"Decaying: {self.decaying} {round(self.decay_fraction*100,2)}%\n Decayed: {self.decayed}\n Healthy: {self.healthy} {round(self.healthy_fraction*100,2)}%\n DELTA_TIME = {round(DELTA_TIME,4)}", start_x=self.center_x, start_y=self.top, color=arcade.color.BLACK, font_size=12, anchor_x="center", anchor_y="bottom", multiline=True, width = 256)
        decay_text.draw()

    @property
    def decay_fraction(self):
        return self.decay_timer / self.decay_time

    @property
    def healthy_fraction(self):
        return self.healthy_timer / self.healthy_time

    @property
    def edible(self):
        return not self.decayed and not self.being_eaten
