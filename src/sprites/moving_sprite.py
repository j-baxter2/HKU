import arcade

class MovingSprite(arcade.Sprite):
    def __init__(self, data: dict):

        # Load sprite data from JSON
        sprite_data = data["spritesheet"]

        sheet_path = sprite_data["path"]
        scale = sprite_data["scale"]

        # Load sprite sheet
        super().__init__(sheet_path, scale)

        # Load sprite sheet textures
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

        # Set the first texture
        if self.textures:
            self.set_texture(0)

        # Initialise hitbox
        self._hit_box_algorithm = 'Simple'
        self.set_hit_box(self.texture.hit_box_points)

        # Load animation data from JSON
        animation_data = data["animation"]

        # Set up animation variables
        self.current_walk_cycle = None

        # Set up animation variables
        self.animation_timer = 0
        self.frame_time = animation_data["frametime"]
        self.walk_cycle_frames = animation_data["walk"]

        # Load movement data from JSON
        self.base_speed = data["speed"]
        self.speed = 0

    def walk_cycle(self, starting_frame: int, ending_frame: int):
        # Loop through the walk cycle frames
        if self.textures:
            self.set_texture(starting_frame)
        for i in range(starting_frame, ending_frame + 1):
            self.set_texture(i)
            yield

    def start_walk_cycle(self, direction: str):
        # Set the walk cycle frames based on the direction
        starting_frame, ending_frame = self.walk_cycle_frames[direction]
        # Start the walk cycle
        self.current_walk_cycle = self.walk_cycle(starting_frame, ending_frame)
        # Reset the animation timer
        self.animation_timer = 0

    def advance_walk_cycle(self, delta_time=0.25):
        # Advance the walk cycle
        self.animation_timer += delta_time
        # Check if it's time to advance the walk cycle
        if self.animation_timer >= self.frame_time:
            self.animation_timer -= self.frame_time  # Reset timer by subtracting frame rate
            # Advance the walk cycle
            if self.current_walk_cycle:
                try:
                    next(self.current_walk_cycle)
                except StopIteration:
                    self.current_walk_cycle = None  # Reset the cycle if it's finished
