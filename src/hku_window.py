import arcade
import arcade.key
from src.data.constants import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE

class MyWindow(arcade.Window):
    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
        self.center_window()
        self.resources_path = "resources/"

    def setup(self):
        super().setup()
        self.set_update_rate(1/60)
