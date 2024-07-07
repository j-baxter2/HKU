import arcade
from views.menu import MenuView

class GameOverView(arcade.View):
    def __init__(self):
        super().__init__()
        self.message = "Game Over"

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text(self.message, self.window.width / 2, self.window.height / 2,
                         arcade.color.WHITE, font_size=50, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            # Assuming there's a MenuView class to return to the main menu
            menu_view = MenuView()
            self.window.show_view(menu_view)
