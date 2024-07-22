import arcade
import json
from src.sprites.following_sprite import MovingSprite
from src.sprites.player import Player
from pyglet.math import Vec2
import random
import math
import json
from src.data.constants import MAP_WIDTH, MAP_HEIGHT, DELTA_TIME
from src.utils.sound import load_sound, play_sound

class Kitty(MovingSprite):
    def __init__(self, id : int, treats: arcade.SpriteList, player: Player):
        with open("resources/data/kitty.json", "r") as file:
            kitty_dict = json.load(file)
        self.kitty_data = kitty_dict[str(id)]

        super().__init__(self.kitty_data)

        self.treats = treats
        self.player = player

        self.hunger = self.kitty_data["hunger"]
        self.treats_eaten = 0

        self.follow_distance = self.kitty_data["follow radius"]
        self.follow_speed_bonus = self.kitty_data["follow speed bonus"]

        self.change_direction_time = self.kitty_data["change direction time"]
        self.random_movement_timer = 0

        self.meow_time = self.kitty_data["meow time"]
        self.meow_name = self.kitty_data["meow name"]
        self.meow_sound = load_sound(self.meow_name, source="hku")
        self.meow_speed = random.uniform(0.75, 1.25)

        self.velocity = Vec2(0, 0)

        self.target_treat = None

        self.meow_timer = 0

        self.fading = False
        self.fade_timer = 0
        self.fade_time = 1

        self.eating = False
        self.eating_timer = 0
        self.eating_time = 1

        self.fleeing = False
        self.fleeing_timer = 0
        self.fleeing_time = 3

    def setup(self):
        self.randomize_velocity()

    def update(self):
        if self.fading:
            self.update_fade()
        else:
            if self.able_to_move:
                self.update_movement()
            self.random_movement_timer += DELTA_TIME
            if not self.eating and not self.fleeing:
                self.locate_treat()
            self.update_animation(delta_time = DELTA_TIME)
            self.update_meow()
            self.handle_treat_collision()
            self.update_fleeing()
            if self.target_treat:
                self.update_eating()
            super().update()

    def update_meow(self):
        self.meow_timer += DELTA_TIME
        if self.should_meow:
            play_sound(self.meow_sound, volume=self.get_volume_from_player_pos(), pan=self.get_pan_from_player_pos(), speed=self.meow_speed)
            self.meow_timer = 0

    def update_fade(self):
        self.fade_timer += DELTA_TIME
        opacity_decrease = 255 * (self.fade_timer / 2)
        self.alpha = max(255 - opacity_decrease, 0)
        if self.fade_timer >= self.fade_time:
            self.fading = False
            self.kill()

    def start_eating(self):
        self.eating = True

    def update_eating(self):
        if self.eating:
            self.eating_timer += DELTA_TIME
            self.target_treat.being_eaten = True
            self.paralyze()
            if self.target_treat.picked_up:
                self.stop_eating(success=False)
                #play cry sound
            elif self.eating_timer >= self.eating_time:
                self.stop_eating()

    def stop_eating(self, success = True):
        self.eating = False
        self.able_to_move = True
        self.eating_timer = 0
        if self.target_treat:
            self.target_treat.being_eaten = False
        if success:
            self.target_treat.kill()
            self.treats_eaten += 1
            #play eating sound
        if self.treats_eaten >= self.hunger:
            self.fading = True
            #play satisfied sound
        self.target_treat = None

    def start_fleeing(self):
        self.stop_eating(success=False)
        self.fleeing = True
        print(f"Eating: {self.eating}")
        print(f"Fleeing: {self.fleeing}")
        print(f"Able to move: {self.able_to_move}")
        #play scared sound

    def update_fleeing(self):
        if self.fleeing:
            self.fleeing_timer += DELTA_TIME
            self.target_treat = None
            if self.fleeing_timer >= self.fleeing_time:
                self.fleeing = False

    def update_movement_direction(self):
        if self.target_treat:
            self.face_treat()
        elif self.should_turn:
            self.randomize_velocity()
            self.random_movement_timer = 0

    def update_movement_speed(self):
        if self.target_treat or self.fleeing:
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

    def handle_treat_collision(self):
        if self.target_treat:
            if arcade.check_for_collision(self, self.target_treat):
                self.start_eating()

    @property
    def animation_direction(self):
        self.velocity = Vec2(self.velocity[0], self.velocity[1])
        angle = self.velocity.heading
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

    @property
    def should_turn(self):
        return self.random_movement_timer >= (self.change_direction_time+random.uniform(-0.1, 5))

    @property
    def should_meow(self):
        return self.meow_timer >= (self.meow_time+random.uniform(-self.meow_time*0.1, self.meow_time))

    def face_treat(self):
        self.velocity = Vec2(self.target_treat.center_x - self.center_x, self.target_treat.center_y - self.center_y)

    def locate_treat(self):
        for treat in self.treats:
            if arcade.get_distance_between_sprites(self, treat) < self.follow_distance and treat.edible:
                self.target_treat = treat
            else:
                self.target_treat = None

    def get_volume_from_player_pos(self):
        distance = arcade.get_distance_between_sprites(self, self.player)
        distance_in_m = distance / 128
        if distance == 0:
            volume = 1
        else:
            volume = 1/(distance_in_m**2)
        return min(max(volume, 0), 1)

    def get_pan_from_player_pos(self):
        angle = arcade.get_angle_radians(self.player.center_x, self.player.center_y, self.center_x, self.center_y)
        return math.sin(angle)
