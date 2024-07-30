import arcade
from pyglet.math import Vec2

class HKUCamera(arcade.Camera2D):
    def __init__(self, viewport_width, viewport_height):
        super().__init__(viewport_width, viewport_height)
