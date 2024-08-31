import arcade
from src.sprites.enemy import BaseEnemy
from src.data.constants import DELTA_TIME

class BloatingEnemy(BaseEnemy):
    def __init__(self, id: int, scene: arcade.Scene):
        self.scene = scene
        super().__init__(id, self.scene)
        self.bloating = False
        self.vulnerable = True

    def setup(self):
        super().setup()

    def update_while_alive(self):
        self.color = arcade.color.PURPLE

    def draw_debug(self):
        super().draw_debug()
