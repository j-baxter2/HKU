import arcade.gui
from views.game import GameView

class MenuView(arcade.View):
    def __init__(self):
        super().__init__()

        self.manager = arcade.gui.UIManager()
        self.v_box = arcade.gui.UIBoxLayout()

        new_game_texture = arcade.load_texture("resources/textures/ui/new_game_button.png")
        settings_texture = arcade.load_texture("resources/textures/ui/settings_button.png")
        quit_texture = arcade.load_texture("resources/textures/ui/quit_button.png")

        new_game_button = arcade.gui.UITextureButton(texture=new_game_texture)
        self.v_box.add(new_game_button.with_space_around(bottom=20))

        settings_button = arcade.gui.UITextureButton(texture=settings_texture)
        self.v_box.add(settings_button.with_space_around(bottom=20))

        quit_button = arcade.gui.UITextureButton(texture=quit_texture)
        self.v_box.add(quit_button.with_space_around(bottom=20))

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x", anchor_y="center_y", child=self.v_box
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

        @settings_button.event("on_click")
        def on_click_quit(self, event):
            arcade.close_window()

    def on_update(self,delta_time):
        self.manager.on_update(delta_time)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.AIR_SUPERIORITY_BLUE)
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        self.manager.draw()
