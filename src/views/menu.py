import arcade.gui
from views.game import GameView
from src.data.constants import UI_FONT, UI_FONT_PATH
from src.data import color

class MenuView(arcade.View):
    def __init__(self):
        super().__init__()

        arcade.load_font(UI_FONT_PATH)

        self.manager = arcade.gui.UIManager()
        self.v_box = arcade.gui.UIBoxLayout()

        title = arcade.gui.UILabel(text="Hungry Kitty Uprising")
        self.v_box.add(title)

        new_game_button = arcade.gui.UIFlatButton(text="play game", width=200)
        self.v_box.add(new_game_button)

        settings_button = arcade.gui.UIFlatButton(text="settings", width=200)
        self.v_box.add(settings_button)

        quit_button = arcade.gui.UIFlatButton(text="quit", width=200)
        self.v_box.add(quit_button)

        self.manager.add(
            arcade.gui.UIAnchorLayout(
                anchor_x="center_x", anchor_y="center_y", children=[self.v_box]
            )
        )

        @new_game_button.event("on_click")
        def on_click_new_game(event):
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)

        @settings_button.event("on_click")
        def on_click_settings(self, event):
            pass

        @quit_button.event("on_click")
        def on_click_quit(self, event):
            arcade.close_window()

    def on_update(self,delta_time):
        self.manager.on_update(delta_time)

    def on_show_view(self):
        arcade.set_background_color(color.LIGHT_BLUE)
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        self.manager.draw()
