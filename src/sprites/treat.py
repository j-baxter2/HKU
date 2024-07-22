import arcade
from src.data.constants import DELTA_TIME

class Treat(arcade.Sprite):
    def __init__(self, image_file, scale=1):
        super().__init__(image_file, scale)
        self.being_eaten = False
        self.picked_up = False
        self.decaying = True
        self.decayed = False

        self.decay_timer = 0
        self.decay_time = 2

    def update(self):
        self.update_decay()
        self.update_color()

    def update_decay(self):
        if self.decaying:
            self.decay_timer += DELTA_TIME
            if self.decay_timer >= self.decay_time:
                self.decayed = True
                self.decaying = False

    def update_color(self):
        if self.decayed:
            self.color = arcade.color.GRAY
        else:
            self.color = arcade.color.WHITE

    @property
    def edible(self):
        return not self.decayed and not self.being_eaten
