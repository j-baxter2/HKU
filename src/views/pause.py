import arcade
import arcade.gui
from src.data import controls

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

        unlocked_moves = self.player.unlocked_moves
        equipped_moves = self.player.equipped_moves

        style = {"font_color": arcade.color.RED}
        quick_attack_button = arcade.gui.UIFlatButton(text="Quick Attack", width=200)
        vbox.add(quick_attack_button)

        special_button = arcade.gui.UIFlatButton(text="Special", width=200)
        vbox.add(special_button)

        heal_button = arcade.gui.UIFlatButton(text="Heal", width=200)
        vbox.add(heal_button)

        scare_button = arcade.gui.UIFlatButton(text="Scare", width=200)
        vbox.add(scare_button)

        back_button = arcade.gui.UIFlatButton(text="Back", width=200)
        vbox.add(back_button)

        self.manager.add(arcade.gui.UIAnchorWidget(anchor_x="center_x", anchor_y="center_y", child=vbox))

        @back_button.event("on_click")
        def on_click_back(event):
            self.window.show_view(self.game_view)

    def set_move(self, slot, move):
        self.game_view.player.equip_move(slot, move)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK[:3]+(128,))
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        self.manager.draw()
