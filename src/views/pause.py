import arcade
import arcade.gui
from src.data import controls
from src.data import color
from src.data.constants import UI_FONT, UI_FONT_PATH

class PauseView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.manager = arcade.gui.UIManager()
        self.player = self.game_view.game_section.player
        self.setup_ui()

    def setup_ui(self):
        self.manager.enable()
        vbox = arcade.gui.UIBoxLayout()

        arcade.load_font(UI_FONT_PATH)

        unlocked_moves = self.player.unlocked_moves
        equipped_moves = self.player.equipped_moves

        style = {"font_name": UI_FONT, "font_size": 20, "normal_bg": color.LIGHT_GREEN, "hovered_bg":color.MID_GREEN, "pressed_bg": color.DARK_GREEN}
        quick_attack_button = arcade.gui.UIFlatButton(text="Quick Attack", width=200, style=style)
        vbox.add(quick_attack_button.with_space_around(bottom=20))

        special_button = arcade.gui.UIFlatButton(text="Special", width=200, style=style)
        vbox.add(special_button.with_space_around(bottom=20))

        heal_button = arcade.gui.UIFlatButton(text="Heal", width=200, style=style)
        vbox.add(heal_button.with_space_around(bottom=20))

        scare_button = arcade.gui.UIFlatButton(text="Scare", width=200, style=style)
        vbox.add(scare_button.with_space_around(bottom=20))

        back_button = arcade.gui.UIFlatButton(text="Back", width=200, style=style)
        vbox.add(back_button.with_space_around(bottom=20))

        self.manager.add(arcade.gui.UIAnchorWidget(anchor_x="center_x", anchor_y="center_y", child=vbox))

        @back_button.event("on_click")
        def on_click_back(event):
            self.window.show_view(self.game_view)

    def set_move(self, slot, move):
        self.game_view.player.equip_move(slot, move)

    def on_show_view(self):
        arcade.set_background_color(color.LIGHT_BLUE)
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        self.manager.draw()
