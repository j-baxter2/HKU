import arcade
import arcade.key
from src.data.constants import WINDOW_TITLE, DELTA_TIME

class MyWindow(arcade.Window):
    def __init__(self):
        super().__init__(fullscreen=True, title=WINDOW_TITLE)
        self.center_window()
        self.set_mouse_visible(True)
        self.views = {}
        self.music_vol = 0.5
        self.sfx_vol = 0.5

    def setup(self):
        super().setup()
        self.set_update_rate(DELTA_TIME)
