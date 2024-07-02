import arcade

class Kitty(arcade.Sprite):
    def __init__(self, image_file, scale=1):
        super().__init__(image_file, scale)
        self.center_x = 0  # Set the initial x position of the kitty
        self.center_y = 0  # Set the initial y position of the kitty

    def update(self):
        # Add any update logic for the kitty here
        pass

    def draw(self):
        # Add any drawing logic for the kitty here
        self.draw()
