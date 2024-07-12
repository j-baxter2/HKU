import arcade
from src.sprites.moving_sprite import MovingSprite
from src.sprites.player import Player
from pyglet.math import Vec2
import random
import math
import json
from src.utils.constants import MAP_WIDTH, MAP_HEIGHT

class FollowingKitty(MovingSprite):
    def __init__(self, id : int, player : Player):
        # Load player data from JSON
        with open("resources/data/kitty.json", "r") as file:
            kitty_dict = json.load(file)
        self.kitty_data = kitty_dict[str(id)]

        self.player = player

        self.hp = self.kitty_data["hp"]

        self.follow_distance = self.kitty_data["follow radius"]
        self.follow_speed_bonus = self.kitty_data["follow speed bonus"]

        self.change_direction_time = self.kitty_data["change direction time"]
        self.random_movement_timer = 0

        self.velocity = Vec2(0, 0)

        self.just_attacked = False
        self.attack_refresh_time = 0

        super().__init__(self.kitty_data)

    def setup(self):
        self.randomize_velocity()

    def update(self):
        self.update_movement()
        self.random_movement_timer += 1/60
        if self.just_attacked:
            self.attack_refresh_time += 1/60
            if self.attack_refresh_time >= 1:
                self.just_attacked = False
                self.attack_refresh_time = 0
        self.update_animation(delta_time = 1/60)
        self.handle_player_collision()
        super().update()

    def update_movement_direction(self):
        #todo: implement treats taking priority over player
        if self.in_range:
            self.face_player()
        elif self.should_turn:
            #set movement direction to random
            self.randomize_velocity()
            self.random_movement_timer = 0

    def update_movement_speed(self):
        if self.in_range:
            self.speed = self.follow_speed_bonus * self.base_speed
        else:
            self.speed = self.base_speed

    def update_movement(self):
        self.update_movement_direction()
        self.velocity = Vec2(self.velocity[0], self.velocity[1])
        self.velocity = self.velocity.normalize()
        self.update_movement_speed()

        self.velocity = self.velocity.scale(self.speed)

        self.velocity = [self.velocity.x, self.velocity.y]

        self.handle_out_of_bounds()

    def handle_out_of_bounds(self):
        if self.center_x < 0 or self.center_x > MAP_WIDTH:
            self.velocity = [self.velocity[0] * -1, self.velocity[1]]
        elif self.center_y < 0 or self.center_y > MAP_HEIGHT:
            self.velocity = [self.velocity[0], self.velocity[1] * -1]

    @property
    def animation_direction(self):
        #get the angle of the velocity vector
        self.velocity = Vec2(self.velocity[0], self.velocity[1])
        angle = self.velocity.heading
        #convert the angle to degrees
        angle = math.degrees(angle)
        if angle < 135 and angle >= 45:
            return "up"
        elif angle < 45 and angle >= -45:
            return "right"
        elif angle < -45 and angle >= -135:
            return "down"
        else:
            return "left"

    def update_animation(self, delta_time):
        if not self.current_walk_cycle:
            if self.animation_direction:
                self.start_walk_cycle(self.animation_direction)
                self.hit_box = self.texture.hit_box_points
        self.advance_walk_cycle()


    def draw_follow_radius(self):
        arcade.draw_circle_outline(self.center_x, self.center_y, self.follow_distance, arcade.color.BLUE, 8)

    def handle_player_collision(self):
       if self.can_attack and arcade.check_for_collision(self, self.player):
           self.player.take_damage(1)
           self.just_attacked = True

    def face_player(self):
        self.velocity = Vec2(self.player.center_x - self.center_x, self.player.center_y - self.center_y)

    def take_damage(self, amount: int):
        self.hp -= amount
        if self.hp <= 0:
            self.kill()

    @property
    def in_range(self):
        return arcade.get_distance_between_sprites(self, self.player) < self.follow_distance

    @property
    def should_turn(self):
        return self.random_movement_timer >= (self.change_direction_time+random.uniform(-0.1, 5))


    def debug_draw(self):
        self.draw_follow_radius()
        self.draw_hit_box()
        arcade.draw_text(f"RMT: {round(self.random_movement_timer,1)}", self.center_x, self.top + 60, arcade.color.RED, 12)
        arcade.draw_text(f"HP: {round(self.hp)}", self.center_x, self.top + 120, arcade.color.RED, 12)

    @property
    def can_attack(self):
        return not self.just_attacked
