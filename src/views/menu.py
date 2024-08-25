import arcade.gui
import json
from views.game import GameView
from src.data.constants import UI_FONT, UI_FONT_PATH
from src.data import color

class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.window.views["menu"] = self
        try:
            with open("resources/saves/savegame.json", "r") as file:
                self.savegame_dict = json.load(file)
            if len(self.savegame_dict) > 0:
                self.save_detected = True
            else:
                self.save_detected = False
        except FileNotFoundError:
            self.save_detected = False

        self.background = arcade.load_texture("resources/textures/ui/landscape.png")

        arcade.load_font(UI_FONT_PATH)


        self.manager = arcade.gui.UIManager()
        self.v_box = arcade.gui.UIBoxLayout()

        style = {"font_name": UI_FONT, "font_size": 20, "normal_bg": color.LIGHT_GREEN, "hovered_bg":color.MID_GREEN, "pressed_bg": color.DARK_GREEN}

        title_sprite = arcade.Sprite("resources/textures/ui/title.png")

        title_widget = arcade.gui.UISpriteWidget(sprite=title_sprite, width=736, height=256)
        self.v_box.add(title_widget.with_space_around(bottom=40))

        play_texture = arcade.load_texture("resources/textures/ui/play_button.png")

        h_play_texture = arcade.load_texture("resources/textures/ui/hovered_play_button.png")

        p_play_texture = arcade.load_texture("resources/textures/ui/pressed_play_button.png")

        play_button = arcade.gui.UITextureButton(texture=play_texture, texture_hovered=h_play_texture, texture_pressed=p_play_texture, scale=2)

        self.v_box.add(play_button.with_space_around(bottom=20))

        resume_button = arcade.gui.UIFlatButton(text="Resume", width=200)
        if self.save_detected:
            self.v_box.add(resume_button.with_space_around(bottom=20))

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
            game_view.from_dict(self.savegame_dict)
            self.window.show_view(game_view)

    def on_update(self,delta_time):
        self.manager.on_update(delta_time)

    def on_show_view(self):
        arcade.set_background_color(color.LIGHT_BLUE)
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            self.window.width, self.window.height,
                                            self.background)
        self.manager.draw()
