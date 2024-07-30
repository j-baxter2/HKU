import arcade
from arcade.types.rect import Viewport
from pyglet.math import Vec2

class HKUCamera(arcade.Camera2D):
    def __init__(self, viewport_width, viewport_height):
        viewport = Viewport(left=0, bottom=viewport_height, width=viewport_width, height=viewport_height)
        super().__init__(viewport=viewport)
