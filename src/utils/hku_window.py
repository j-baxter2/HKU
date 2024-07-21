import arcade
import arcade.key
from src.data.constants import WINDOW_TITLE, DELTA_TIME

class MyWindow(arcade.Window):
    def __init__(self):
        super().__init__(fullscreen=True, title=WINDOW_TITLE)
        self.center_window()
        self.set_mouse_visible(True)

    def setup_cursor(self):
        cursor_texture = arcade.load_texture("resources/textures/cursor_image.png")
        self.set_mouse_cursor(cursor_texture)

    def setup(self):
        super().setup()
        self.setup_cursor()
        self.set_update_rate(DELTA_TIME)
