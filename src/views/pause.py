import arcade
import arcade.gui
import json
from src.data import controls
from src.data import color
from src.data.constants import UI_FONT, UI_FONT_PATH, SOUND_EFFECT_VOL
from src.utils.sound import load_sound, play_sound

class PauseView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view

        self.manager = arcade.gui.UIManager()
        self.setup_ui()

    def setup_ui(self):
        self.manager.enable()
        vbox = arcade.gui.UIBoxLayout()

        arcade.load_font(UI_FONT_PATH)

        style = {
            "font_name": UI_FONT, "font_size": 20,
            "normal": {
                "bg": color.LIGHT_GREEN
            },
            "hovered": {
                "bg": color.MID_GREEN
            },
            "pressed": {
                "bg": color.DARK_GREEN
            }
        }
        resume_button = arcade.gui.UIFlatButton(text="Resume", width=200, style=style)
        vbox.add(resume_button.with_space_around(bottom=20))

        quit_button = arcade.gui.UIFlatButton(text="Quit", width=200, style=style)
        vbox.add(quit_button.with_space_around(bottom=20))

        self.manager.add(arcade.gui.UIAnchorWidget(anchor_x="center_x", anchor_y="center_y", child=vbox))

        @resume_button.event("on_click")
        def on_click_resume(event):
            self.window.show_view(self.game_view)

        @quit_button.event("on_click")
        def on_click_quit(event):
            self.window.show_view(self.game_view.main_menu)

    def on_key_press(self, key: int, modifiers: int):
        if key == controls.PAUSE:
            self.window.show_view(self.game_view)

    def on_show_view(self):
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        self.game_view.game_section.update_camera()
        self.game_view.game_section.on_draw()
        self.game_view.ui_section.camera.use()
        arcade.draw_lrtb_rectangle_filled(0, self.window.width, self.window.height, 0, arcade.color.BLACK[:3] + (128,))
        self.manager.draw()

class MoveSelectView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.quick_attack_view = MoveView(self.game_view, self, "quick attack")
        self.special_view = MoveView(self.game_view, self, "special")
        self.heal_view = MoveView(self.game_view, self, "heal")
        self.scare_view = MoveView(self.game_view, self, "scare")

        self.game_saved = False

        self.save_sound = load_sound("coin1")

        self.manager = arcade.gui.UIManager()
        self.setup_ui()

    def setup_ui(self):
        self.manager.enable()
        vbox = arcade.gui.UIBoxLayout()

        arcade.load_font(UI_FONT_PATH)

        style = {
            "font_name": UI_FONT, "font_size": 20,
            "normal": {
                "bg": color.LIGHT_GREEN
            },
            "hovered": {
                "bg": color.MID_GREEN
            },
            "pressed": {
                "bg": color.DARK_GREEN
            }
        }

        self.save_button = arcade.gui.UIFlatButton(text="save", width=200, style=style)
        vbox.add(self.save_button.with_space_around(bottom=20))

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

        @self.save_button.event("on_click")
        def on_click_save(event):
            play_sound(self.save_sound, volume=SOUND_EFFECT_VOL)
            self.save_game_view()

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


    def save_game_view(self):
        with open('resources/saves/savegame.json', 'w') as json_file:
            json.dump(self.game_view.to_dict(), json_file, indent=4)
        self.game_saved = True

    def on_key_press(self, key: int, modifiers: int):
        if key == controls.PAUSE:
            self.window.show_view(self.game_view)

    def on_show_view(self):
        self.game_saved = False
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        self.game_view.game_section.on_draw()
        self.game_view.ui_section.camera.use()
        arcade.draw_lrtb_rectangle_filled(0, self.window.width, self.window.height, 0, arcade.color.BLACK[:3] + (128,))
        if self.game_saved == True:
            saved_text = arcade.Text("SAVED!", start_x=self.save_button.right+20, start_y=self.save_button.center_y, anchor_y="center", font_name=UI_FONT, font_size=20,)
            saved_text.draw()
        self.manager.draw()

class MoveView(arcade.View):
    def __init__(self, game_view, move_select_view, slot: str):
        super().__init__()
        self.game_view = game_view
        self.move_select_view = move_select_view
        self.slot = slot
        self.alt_slot = f"alt {slot}"
        self.manager = arcade.gui.UIManager()
        self.player = self.game_view.game_section.player
        self.unlocked_slot_moves = []
        self.move_buttons = {}
        self.alt_move_buttons = {}
        self.setup_ui()

    def setup_ui(self):
        self.manager.enable()

        super_vbox = arcade.gui.UIBoxLayout(vertical=True, align="center")

        hbox = arcade.gui.UIBoxLayout(vertical=False, space_between=20)

        primary_vbox = arcade.gui.UIBoxLayout(vertical=True, align="center")
        alt_vbox = arcade.gui.UIBoxLayout(vertical=True, align="center")

        arcade.load_font(UI_FONT_PATH)

        style = {"font_name": UI_FONT, "font_size": 20, "normal_bg": color.LIGHT_GREEN, "hovered_bg": color.MID_GREEN, "pressed_bg": color.DARK_GREEN}

        primary_label = arcade.gui.UILabel(text="Primary", anchor_x="left", width=200, font_name=UI_FONT, font_size=20, text_color=arcade.color.WHITE)
        primary_vbox.add(primary_label.with_space_around(bottom=20))

        alt_label = arcade.gui.UILabel(text="ALT", width=200, font_name=UI_FONT, font_size=20, text_color=arcade.color.WHITE)
        alt_vbox.add(alt_label.with_space_around(bottom=20))

        for move in self.player.unlocked_moves:
            if move.slot == self.slot:
                self.unlocked_slot_moves.append(move)

        for move in self.unlocked_slot_moves:
            primary_button = arcade.gui.UIFlatButton(width=200, style=style)
            primary_button.text = f"{move.name}"
            primary_vbox.add(primary_button.with_space_around(bottom=20))
            primary_button.on_click = lambda event, move=move: self.on_click_move(event, move, self.slot)
            self.move_buttons[move.name] = primary_button

            alt_button = arcade.gui.UIFlatButton(width=200, style=style)
            alt_button.text = f"{move.name}"
            alt_vbox.add(alt_button.with_space_around(bottom=20))
            alt_button.on_click = lambda event, move=move: self.on_click_move(event, move, self.alt_slot)
            self.alt_move_buttons[move.name] = alt_button

        back_button = arcade.gui.UIFlatButton(text="Back", width=200, style=style)

        hbox.add(primary_vbox)
        hbox.add(alt_vbox)

        super_vbox.add(hbox)
        super_vbox.add(back_button)

        self.manager.add(arcade.gui.UIAnchorWidget(anchor_x="center_x", anchor_y="center_y", child=super_vbox))

        @back_button.event("on_click")
        def on_click_back(event):
            self.window.show_view(self.move_select_view)

    def on_click_move(self, event, move, slot):
        self.player.equip_move(slot=slot, move=move)

    def on_key_press(self, key: int, modifiers: int):
        if key == controls.PAUSE:
            self.window.show_view(self.game_view)

    def on_show_view(self):
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        self.game_view.game_section.update_camera()
        self.game_view.game_section.on_draw()
        self.game_view.ui_section.camera.use()
        arcade.draw_lrtb_rectangle_filled(0, self.window.width, self.window.height, 0, arcade.color.BLACK[:3] + (128,))
        for move in self.unlocked_slot_moves:
            if move == self.player.equipped_moves[self.slot]:
                button = self.move_buttons[move.name]
                arcade.draw_circle_filled(center_x=button.left-32, center_y=button.center_y, radius=16, color=arcade.color.RED)
            elif move == self.player.equipped_moves[self.alt_slot]:
                button = self.alt_move_buttons[move.name]
                arcade.draw_circle_filled(center_x=button.right+32, center_y=button.center_y, radius=16, color=arcade.color.RED)
        self.manager.draw()
