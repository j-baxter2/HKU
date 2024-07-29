import arcade
import arcade.gui
from src.data import controls
from src.data import color
from src.data.constants import UI_FONT, UI_FONT_PATH

class PauseView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.quick_attack_view = MoveView(self.game_view, self, "quick attack")
        self.special_view = MoveView(self.game_view, self, "special")
        self.heal_view = MoveView(self.game_view, self, "heal")
        self.scare_view = MoveView(self.game_view, self, "scare")

        self.manager = arcade.gui.UIManager()
        self.setup_ui()

    def setup_ui(self):
        self.manager.enable()
        vbox = arcade.gui.UIBoxLayout()

        arcade.load_font(UI_FONT_PATH)

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

        @quick_attack_button.event("on_click")
        def on_click_quick_attack(event):
            self.window.show_view(self.quick_attack_view)

        @special_button.event("on_click")
        def on_click_special(event):
            self.window.show_view(self.special_view)

        @heal_button.event("on_click")
        def on_click_heal(event):
            self.window.show_view(self.heal_view)

        @scare_button.event("on_click")
        def on_click_scare(event):
            self.window.show_view(self.scare_view)

        @back_button.event("on_click")
        def on_click_back(event):
            self.window.show_view(self.game_view)

    def on_key_press(self, key: int, modifiers: int):
        if key == controls.PAUSE:
            self.window.show_view(self.game_view)

    def on_show_view(self):
        arcade.set_background_color(color.LIGHT_BLUE)
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        self.manager.draw()

class MoveView(arcade.View):
    def __init__(self, game_view, pause_view, slot: str):
        super().__init__()
        self.game_view = game_view
        self.pause_view = pause_view
        self.slot = slot
        self.manager = arcade.gui.UIManager()
        self.player = self.game_view.game_section.player
        self.unlocked_slot_moves = []
        self.setup_ui()

    def setup_ui(self):
        self.manager.enable()
        vbox = arcade.gui.UIBoxLayout()

        arcade.load_font(UI_FONT_PATH)

        for move in self.player.unlocked_moves:
            if move.slot == self.slot:
                self.unlocked_slot_moves.append(move)

        style = {"font_name": UI_FONT, "font_size": 20, "normal_bg": color.LIGHT_GREEN, "hovered_bg":color.MID_GREEN, "pressed_bg": color.DARK_GREEN}

        for move in self.unlocked_slot_moves:
            move_button = arcade.gui.UIFlatButton(text=f"{move.name}", width=200, style=style)
            vbox.add(move_button.with_space_around(bottom=20))

            move_button.on_click = lambda event, move=move: self.on_click_move(event, move)

        self.manager.add(arcade.gui.UIAnchorWidget(anchor_x="center_x", anchor_y="center_y", child=vbox))

    def on_click_move(self, event, move):
        self.player.equip_move(slot=self.slot, move=move)
        self.window.show_view(self.pause_view)

    def on_key_press(self, key: int, modifiers: int):
        if key == controls.PAUSE:
            self.window.show_view(self.game_view)

    def on_show_view(self):
        arcade.set_background_color(color.LIGHT_BLUE)
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        self.manager.draw()
