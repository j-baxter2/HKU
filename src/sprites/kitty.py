import arcade
import json
from src.sprites.following_sprite import FollowingSprite
from src.sprites.player import Player
from pyglet.math import Vec2
import random
import math
import json
from src.data.constants import MAP_WIDTH, MAP_HEIGHT, DELTA_TIME
from src.utils.sound import load_sound, play_sound

class Kitty(FollowingSprite):
    def __init__(self, id : int, treats: arcade.SpriteList, player: Player):
        with open("resources/data/kitty.json", "r") as file:
            kitty_dict = json.load(file)
        self.kitty_data = kitty_dict[str(id)]
        self.player = player

        super().__init__(self.kitty_data, self.player)

        self.treats = treats

        self.hunger = self.kitty_data["hunger"]
        self.treats_eaten = 0

        self.meow_time = self.kitty_data["meow time"]
        self.meow_name = self.kitty_data["meow name"]
        self.meow_sound = load_sound(self.meow_name, source="hku")
        self.meow_speed = random.uniform(0.5, 1.5)

        self.target_treat = None

        self.meow_timer = 0

        self.eating = False
        self.eating_timer = 0
        self.eating_time = 1

        self.fleeing = False
        self.fleeing_timer = 0
        self.fleeing_time = 3

    def take_damage(self, damage):
        self.start_fleeing()

    @property
    def is_dead(self):
        return

    def setup(self):
        self.randomize_velocity()

    def update_while_alive(self):
        if not self.eating and not self.fleeing:
            self.locate_treat()
            self.update_meow()
            self.handle_treat_collision()
            self.update_fleeing()
        if self.target_treat:
            self.update_eating()

    def update_meow(self):
        self.meow_timer += DELTA_TIME
        if self.should_meow:
            play_sound(self.meow_sound, volume=self.get_volume_from_player_pos(), pan=self.get_pan_from_player_pos(), speed=self.meow_speed)
            self.meow_timer = 0

    def start_eating(self):
        self.eating = True
        self.paralyze()
        self.eating_timer = 0

    def update_eating(self):
        if self.eating:
            if self.target_treat.picked_up or self.target_treat.decayed:
                self.stop_eating(success=False)
                #play cry sound
                return
            self.eating_timer += DELTA_TIME
            self.target_treat.being_eaten = True
            if self.eating_timer >= self.eating_time:
                self.stop_eating()

    def stop_eating(self, success = True):
        self.eating = False
        self.able_to_move = True
        self.eating_timer = 0
        self.randomize_velocity()
        if self.target_treat:
            self.target_treat.being_eaten = False
        if success:
            self.target_treat.kill()
            self.treats_eaten += 1
            #play eating sound
        if self.treats_eaten >= self.hunger:
            self.paralyze()
            self.fading = True
            #play satisfied sound
        self.target_treat = None

    def start_fleeing(self):
        self.stop_eating(success=False)
        self.fleeing = True
        self.fleeing_timer = 0
        #play scared sound

    def update_fleeing(self):
        if self.fleeing:
            self.fleeing_timer += DELTA_TIME
            if self.fleeing_timer >= self.fleeing_time:
                self.fleeing = False
                self.fleeing_timer = 0

    def locate_treat(self):
        for treat in self.treats:
            if arcade.get_distance_between_sprites(self, treat) < self.follow_distance and treat.edible:
                self.target_treat = treat
            else:
                self.target_treat = None

    def handle_treat_collision(self):
        if self.target_treat:
            if arcade.check_for_collision(self, self.target_treat) and not self.eating:
                self.start_eating()

    def face_treat(self):
        self.velocity = Vec2(self.target_treat.center_x - self.center_x, self.target_treat.center_y - self.center_y)

    def face_away_from_treat(self):
        self.velocity = Vec2(self.center_x - self.target_treat.center_x, self.center_y - self.target_treat.center_y)

    def update_movement_direction(self):
        if self.target_treat and not self.fleeing:
            self.face_treat()
        elif self.should_turn:
            self.randomize_velocity()
            self.random_movement_timer = 0

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
        super().update_animation(delta_time)

    @property
    def should_turn(self):
        return self.random_movement_timer >= (self.random_movement_time+random.uniform(-0.1, 5))

    @property
    def should_sprint(self):
        return self.target_treat or self.fleeing

    @property
    def should_meow(self):
        return self.meow_timer >= (self.meow_time+random.uniform(-self.meow_time*0.5, self.meow_time*3))


    def get_volume_from_player_pos(self):
        distance = arcade.get_distance_between_sprites(self, self.player)
        distance_in_m = distance / 128
        if distance == 0:
            volume = 1
        else:
            volume = 1/(distance_in_m)
        return min(max(volume, 0), 1)

    def get_pan_from_player_pos(self):
        angle = arcade.get_angle_radians(self.player.center_x, self.player.center_y, self.center_x, self.center_y)
        return math.sin(angle)

    def debug_draw(self):
        super().debug_draw()
        arcade.draw_text(f"fleeing: {self.fleeing} eating: {self.eating}", self.center_x, self.center_y-100, arcade.color.BLACK, 12)
        arcade.draw_text(f"eatingprogress: {round(self.eating_timer/self.eating_time,1)}", self.center_x, self.center_y+100, arcade.color.BLACK, 12)
        arcade.draw_text(f"fleeingprogress: {round(self.fleeing_timer/self.fleeing_time,1)}", self.center_x, self.center_y+200, arcade.color.BLACK, 12)
