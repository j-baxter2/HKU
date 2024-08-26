import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import arcade
from views.menu import MenuView

def main():
    from utils.hku_window import MyWindow
    window = MyWindow()
    window.setup()
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()

if __name__ == "__main__":
    main()
