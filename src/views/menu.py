import arcade.gui
import json
from views.game import GameView
from src.data.constants import UI_FONT, UI_FONT_PATH
from src.data import color

class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.window.views["menu"] = self
        self.save_detected = False

        self.background = arcade.load_texture("resources/textures/ui/landscape.png")

        arcade.load_font(UI_FONT_PATH)

    def setup_ui(self):
        self.manager = arcade.gui.UIManager()
        self.v_box = arcade.gui.UIBoxLayout()

        style = arcade.get_window().button_style

        title_sprite = arcade.Sprite("resources/textures/ui/title.png")

        title_widget = arcade.gui.UISpriteWidget(sprite=title_sprite, width=736, height=256)
        self.v_box.add(title_widget.with_space_around(bottom=40))

        play_button = arcade.gui.UIFlatButton(text="New", width=256, style=style)
        self.v_box.add(play_button.with_space_around(bottom=20))

        resume_button = arcade.gui.UIFlatButton(text="Load", width=256, style=style)
        self.check_for_save()
        if self.save_detected:
            self.v_box.add(resume_button.with_space_around(bottom=20))

        quit_button = arcade.gui.UIFlatButton(text="Quit", width=256, style=style)
        self.v_box.add(quit_button.with_space_around(bottom=20))

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x", anchor_y="center_y", child=self.v_box
            )
        )

        @play_button.event("on_click")
        def on_click_play(event):
            game_view = GameView()
            game_view.main_menu = self
            game_view.setup()
            self.window.show_view(game_view)

        @resume_button.event("on_click")
        def on_click_resume(event):
            game_view = GameView()
            game_view.main_menu = self
            game_view.setup()
            with open("resources/saves/savegame.json", "r") as file:
                self.savegame_dict = json.load(file)
            game_view.from_dict(self.savegame_dict)
            self.window.show_view(game_view)

        @quit_button.event("on_click")
        def on_click_resume(event):
            arcade.close_window()

    def on_update(self,delta_time):
        self.manager.on_update(delta_time)

    def on_show_view(self):
        arcade.set_background_color(color.LIGHT_BLUE)
        self.setup_ui()
        self.manager.enable()

    def on_hide_view(self):
        self.v_box.clear()
        self.manager.disable()

    def on_draw(self):
        self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            self.window.width, self.window.height,
                                            self.background)
        self.manager.draw()

    def check_for_save(self):
        try:
            with open("resources/saves/savegame.json", "r") as file:
                self.savegame_dict = json.load(file)
            if len(self.savegame_dict) > 0:
                self.save_detected = True
            else:
                self.save_detected = False
        except FileNotFoundError:
            self.save_detected = False
