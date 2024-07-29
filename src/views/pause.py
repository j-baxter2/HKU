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
        self.alt_slot = f"alt {slot}"
        self.manager = arcade.gui.UIManager()
        self.player = self.game_view.game_section.player
        self.unlocked_slot_moves = []
        self.setup_ui()

    def setup_ui(self):
        self.manager.enable()

        hbox = arcade.gui.UIBoxLayout(vertical=False, space_between=20)

        primary_vbox = arcade.gui.UIBoxLayout(vertical=True, align="center")
        alt_vbox = arcade.gui.UIBoxLayout(vertical=True, align="center")

        arcade.load_font(UI_FONT_PATH)

        style = {"font_name": UI_FONT, "font_size": 20, "normal_bg": color.LIGHT_GREEN, "hovered_bg": color.MID_GREEN, "pressed_bg": color.DARK_GREEN}

        primary_label = arcade.gui.UILabel(text="Primary", width=200, font_name=UI_FONT, font_size=20, text_color=arcade.color.BLACK)
        primary_vbox.add(primary_label.with_space_around(bottom=20))

        alt_label = arcade.gui.UILabel(text="ALT", width=200, font_name=UI_FONT, font_size=20, text_color=arcade.color.BLACK)
        alt_vbox.add(alt_label.with_space_around(bottom=20))

        for move in self.player.unlocked_moves:
            if move.slot == self.slot:
                self.unlocked_slot_moves.append(move)

        for move in self.unlocked_slot_moves:
            primary_button = arcade.gui.UIFlatButton(width=200, style=style)
            if move == self.player.equipped_moves[self.slot]:
                primary_button.text = f"{move.name} (equipped)"
            else:
                primary_button.text = f"{move.name}"
            primary_vbox.add(primary_button.with_space_around(bottom=20))
            primary_button.on_click = lambda event, move=move: self.on_click_move(event, move, self.slot)

            alt_button = arcade.gui.UIFlatButton(width=200, style=style)
            if move == self.player.equipped_moves[self.alt_slot]:
                alt_button.text = f"{move.name} (alt equipped)"
            else:
                alt_button.text = f"{move.name}"
            alt_vbox.add(alt_button.with_space_around(bottom=20))
            alt_button.on_click = lambda event, move=move: self.on_click_move(event, move, self.alt_slot)

        hbox.add(primary_vbox)
        hbox.add(alt_vbox)

        self.manager.add(arcade.gui.UIAnchorWidget(anchor_x="center_x", anchor_y="center_y", child=hbox))


    def on_click_move(self, event, move, slot):
        self.player.equip_move(slot=slot, move=move)
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
