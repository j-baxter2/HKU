import arcade
from src.sprites.enemy import BaseEnemy
from src.data.constants import DELTA_TIME

class BloatingEnemy(BaseEnemy):
    def __init__(self, id: int, scene: arcade.Scene):
        self.scene = scene
        super().__init__(id, self.scene)

    def setup(self):
        super().setup()
        self.set_texture(0)

    def update_while_alive(self):
        self.color = arcade.color.YELLOW

    def draw_debug(self):
        super().draw_debug()
