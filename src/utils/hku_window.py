import arcade
import arcade.key
from src.data.constants import WINDOW_TITLE

class MyWindow(arcade.Window):
    def __init__(self):
        super().__init__(fullscreen=True, title=WINDOW_TITLE)
        self.center_window()
        self.set_mouse_visible(True)
        self.resources_path = "resources/"

    def setup_cursor(self):
        cursor_texture = arcade.load_texture("resources/textures/cursor_image.png")
        # Set the custom cursor
        self.set_mouse_cursor(cursor_texture)

    def setup(self):
        super().setup()
        self.setup_cursor()
        self.set_update_rate(1/60)
