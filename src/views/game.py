import arcade
import arcade.color
from src.sprites.player import Player
from src.data import controls
from pyglet.math import Vec2

class GameSection(arcade.Section):
    def __init__(self, left: int, bottom: int, width: int, height: int,
                 **kwargs):
        super().__init__(left, bottom, width, height,
                          **kwargs)
        self.player_sprite = None
        self.player_sprite_list = None

        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.sprint_pressed = False

        self.wallSpriteList = None

        # Physics engine
        self.physicsEngine = None

        self.camera = arcade.Camera(self.width, self.height)


    def setup(self):
        self.player_sprite = Player(id=0)

        self.player_sprite.center_x = self.width//2
        self.player_sprite.center_y = self.height//2

        self.player_sprite_list = arcade.SpriteList()
        self.player_sprite_list.append(self.player_sprite)

        self.wallSpriteList = arcade.SpriteList(use_spatial_hash=True)

        for x in range(0, int(self.width), 64):
            wall = arcade.Sprite("resources/textures/wall.png")
            wall.center_x = x
            wall.center_y = self.bottom+self.height//2
            self.wallSpriteList.append(wall)

        self.physicsEngine = arcade.PhysicsEngineSimple(
            self.player_sprite,
            self.wallSpriteList
        )


    def on_update(self, delta_time: float):

        self.update_movement()
        self.update_animation()

        # Check if sprinting and update stamina
        self.player_sprite.sprinting = self.sprint_pressed
        self.player_sprite.update_stamina(delta_time)

        self.physicsEngine.update()

    def on_draw(self):
        self.player_sprite.draw()
        self.wallSpriteList.draw()

    def on_key_press(self, key, modifiers):
        if key == controls.UP:
            self.up_pressed = True
        elif key == controls.DOWN:
            self.down_pressed = True
        elif key == controls.LEFT:
            self.left_pressed = True
        elif key == controls.RIGHT:
            self.right_pressed = True
        elif key == controls.SPRINT:
            self.sprint_pressed = True

    def on_key_release(self, key, modifiers):
        if key == controls.UP:
            self.up_pressed = False
        elif key == controls.DOWN:
            self.down_pressed = False
        elif key == controls.LEFT:
            self.left_pressed = False
        elif key == controls.RIGHT:
            self.right_pressed = False
        elif key == controls.SPRINT:
            self.sprint_pressed = False

    def update_movement_direction(self):
        self.player_sprite.velocity = Vec2(0, 0)
        if self.up_pressed:
            self.player_sprite.velocity += Vec2(0, 1)
        if self.down_pressed:
            self.player_sprite.velocity -= Vec2(0, 1)
        if self.left_pressed:
            self.player_sprite.velocity -= Vec2(1, 0)
        if self.right_pressed:
            self.player_sprite.velocity += Vec2(1, 0)

    def update_movement_speed(self):
        if self.player_sprite.stamina > 0:
            if self.sprint_pressed:
                self.player_sprite.speed = self.player_sprite.base_speed * self.player_sprite.sprint_multiplier
            else:
                self.player_sprite.speed = self.player_sprite.base_speed
        else:
            self.player_sprite.speed = self.player_sprite.base_speed

    def update_movement(self):
        self.update_movement_direction()
        self.player_sprite.velocity = self.player_sprite.velocity.normalize()
        self.update_movement_speed()

        self.player_sprite.velocity = self.player_sprite.velocity.scale(self.player_sprite.speed)
        self.player_sprite.velocity = [self.player_sprite.velocity.x, self.player_sprite.velocity.y]

    def update_animation(self):
        if not self.player_sprite.current_walk_cycle:
            if self.up_pressed:
                self.player_sprite.start_walk_cycle('up')
            elif self.down_pressed:
                self.player_sprite.start_walk_cycle('down')
            elif self.left_pressed:
                self.player_sprite.start_walk_cycle('left')
            elif self.right_pressed:
                self.player_sprite.start_walk_cycle('right')
        self.player_sprite.advance_walk_cycle()

class UISection(arcade.Section):
    def __init__(self, left: int, bottom: int, width: int, height: int, **kwargs):
        super().__init__(left, bottom, width, height,
                          **kwargs)
        self.player = None

    def setup(self):
        self.player = self.get_player()

    def on_update(self, delta_time: float):
        pass

    def on_draw(self):
        self.draw_stamina_bar()

    def draw_stamina_bar(self):
        if self.player:
            # Calculate the width of the filled portion of the stamina bar
            filled_width = (self.player.stamina / self.player.max_stamina) * 100
            # Draw the background of the stamina bar
            arcade.draw_rectangle_filled(center_x=self.left + 100,
                                         center_y=self.bottom + 70,
                                         width=100,
                                         height=10,
                                         color=arcade.color.BLACK)
            # Draw the filled portion of the stamina bar
            arcade.draw_rectangle_filled(center_x=self.left + 100 - (50 - filled_width / 2),
                                         center_y=self.bottom + 70,
                                         width=filled_width,
                                         height=10,
                                         color=arcade.color.GREEN)

    def get_player(self):
        return self.view.game_section.player_sprite

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.game_section = GameSection(0.05*self.window.width, 0.2*self.window.height,
                                       0.9*self.window.width, 0.6*self.window.height, accept_keyboard_events=True)
        self.ui_section = UISection(0, 0,
                                   self.window.width, self.window.height)

        self.sectionManager = arcade.SectionManager(self)
        self.sectionManager.add_section(self.game_section)
        self.sectionManager.add_section(self.ui_section)

        self.player_sprite = None

    def setup(self):

        self.game_section.setup()
        self.ui_section.setup()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.ANDROID_GREEN)

    def on_draw(self):
        arcade.start_render()
        #draw a rectangle bounding the game section
        arcade.draw_lrtb_rectangle_outline(self.game_section.left, self.game_section.right,
                                      self.game_section.top, self.game_section.bottom,
                                      arcade.color.BLACK, 3)
        self.game_section.on_draw()
        self.ui_section.on_draw()

    def on_update(self, delta_time: float):
        self.game_section.on_update(delta_time)
        self.ui_section.on_update(delta_time)

    def on_key_press(self, key, modifiers):
        self.game_section.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        self.game_section.on_key_release(key, modifiers)
