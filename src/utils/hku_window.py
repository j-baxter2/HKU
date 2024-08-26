import arcade
import arcade.key
from src.data.constants import WINDOW_TITLE, DELTA_TIME, UI_FONT
import src.data.color as color

class MyWindow(arcade.Window):
    def __init__(self):
        super().__init__(fullscreen=True, title=WINDOW_TITLE)
        self.center_window()
        self.set_mouse_visible(True)
        self.views = {}
        self.music_vol = 0.5
        self.sfx_vol = 0.5
        self.button_style = None
        self.slider_style = None

    def setup(self):
        self.set_update_rate(DELTA_TIME)
        self.button_style = {
            "font_name": UI_FONT, "font_size": 20,
            "font_color": arcade.color.BLACK,
            "bg_color": color.LIGHT_GREEN,
            "border_color": color.MID_GREEN,
            "bg_color_hovered": color.MID_GREEN,
            "bg_color_pressed": color.DARK_GREEN,
            "border_color_pressed": arcade.color.BLACK
        }
        self.slider_style = {
            "normal_filled_bar": color.LIGHT_GREEN,
            "normal_unfilled_bar":
            arcade.color.WHITE,
            "hovered_filled_bar": color.MID_GREEN,
            "hovered_unfilled_bar":
            color.LIGHT_GREEN,
            "pressed_filled_bar": color.MID_GREEN,
            "pressed_unfilled_bar":
            color.LIGHT_GREEN,
        }
