import arcade
from src.data.constants import SPRITE_SIZE

class MovingSprite(arcade.Sprite):
    def __init__(self, data: dict):

        sprite_data = data["spritesheet"]

        sheet_path = sprite_data["path"]
        scale = sprite_data["scale"]

        super().__init__(sheet_path, scale)

        columns = sprite_data["columns"]
        count = sprite_data["count"]
        width = sprite_data["width"]
        height = sprite_data["height"]

        self.textures = arcade.load_spritesheet(
            sheet_path,
            sprite_width=width,
            sprite_height=height,
            columns=columns,
            count=count,
        )

        if self.textures:
            self.set_texture(0)

        animation_data = data["animation"]

        self.current_walk_cycle = None
        self.animation_timer = 0
        self.frame_rate = animation_data["framerate"]
        self.walk_cycle_frames = animation_data["walk"]

    def walk_cycle(self, starting_frame: int, ending_frame: int):
        if self.textures:
            self.set_texture(starting_frame)
        for i in range(starting_frame, ending_frame + 1):
            self.set_texture(i)
            yield

    def start_walk_cycle(self, direction: str):
        starting_frame, ending_frame = self.walk_cycle_frames[direction]
        self.current_walk_cycle = self.walk_cycle(starting_frame, ending_frame)
        self.animation_timer = 0

    def advance_walk_cycle(self, delta_time=0.25):
        self.animation_timer += delta_time
        if self.animation_timer >= self.frame_rate:
            self.animation_timer -= self.frame_rate  # Reset timer by subtracting frame rate
            if self.current_walk_cycle:
                try:
                    next(self.current_walk_cycle)
                except StopIteration:
                    self.current_walk_cycle = None  # Reset the cycle if it's finished
