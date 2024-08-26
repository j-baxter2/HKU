import arcade
import json
from src.sprites.following_sprite import FollowingSprite
from src.sprites.player import Player
from src.sprites.treat import Treat
from pyglet.math import Vec2
import random
import math
import json
from src.data.constants import MAP_WIDTH, MAP_HEIGHT, DELTA_TIME
from src.utils.sound import load_sound, play_sound

class Kitty(FollowingSprite):
    def __init__(self, id : int, scene: arcade.Scene):
        with open("resources/data/kitty.json", "r") as file:
            kitty_dict = json.load(file)
        self.kitty_data = kitty_dict[str(id)]
        self.scene = scene

        super().__init__(self.kitty_data, self.scene)

        self.treats = self.scene.get_sprite_list("Treat")

        self.hunger = self.kitty_data["hunger"]
        self.treats_eaten = 0

        self.meow_time = self.kitty_data["meow time"]
        self.meow_name = self.kitty_data["meow name"]
        self.meow_sound = load_sound(self.meow_name, source="hku")
        self.meow_speed = random.uniform(0.5, 1.5)

        self.fed_sound = load_sound("yay", source="hku")
        self.swallow_sound = load_sound("cat_swallow", source="hku")
        self.stop_eating_sound = load_sound("cat_dissapointed", source="hku")
        self.stop_eating_sound2 = load_sound("lose4")
        self.eating_sound = load_sound("nom", source="hku")
        self.yelp_sound = load_sound("cat_yelp", source="hku")

        self.target_treat = None

        self.meow_timer = 0

        self.eating = False
        self.eating_timer = 0
        self.eating_time = 1

        self.fleeing = False
        self.fleeing_timer = 0
        self.fleeing_time = 3

        self.need_second_timer = 0
        self.need_second_time = 3

        self.fade_texture_index = self.kitty_data["spritesheet"]["fade texture"]
        self.sitting_frames = self.kitty_data["animation"]["sitting"]

    def take_damage(self, damage):
        play_sound(self.yelp_sound, volume=self.get_volume_from_player_pos(), pan=self.get_pan_from_player_pos())
        self.stop_eating(success=False)
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
        self.update_treats()
        self.update_need_second()
        if self.target_treat:
            self.update_eating()

    def update_treats(self):
        self.treats = self.scene.get_sprite_list("Treat")

    def update_need_second(self):
        if self.treats_eaten == 1:
            self.need_second_timer += DELTA_TIME
            blue = 255*(self.need_second_timer/self.need_second_time)
            self.color = [255, 255, min(blue, 255)]
            if self.need_second_timer >= self.need_second_time:
                play_sound(self.stop_eating_sound, volume=self.get_volume_from_player_pos(), pan=self.get_pan_from_player_pos())
                play_sound(self.stop_eating_sound2, volume=self.get_volume_from_player_pos(), pan=self.get_pan_from_player_pos())
                self.color = arcade.color.WHITE
                self.treats_eaten = 0
                edge_margin = 64
                x = random.uniform(edge_margin+1304, MAP_WIDTH - edge_margin)
                y = random.uniform(edge_margin+1823, MAP_HEIGHT - edge_margin)

                treat = Treat(scene=self.scene, image_file="resources/spritesheets/treat.png", scale=4, decayed=True)
                treat.position = (x, y)
                self.scene.add_sprite("Treat", treat)
                self.need_second_timer = 0

    def update_meow(self):
        self.meow_timer += DELTA_TIME
        if self.should_meow:
            play_sound(self.meow_sound, volume=self.get_volume_from_player_pos(), pan=self.get_pan_from_player_pos(), speed=self.meow_speed)
            self.meow_timer = 0

    def start_eating(self):
        self.eating = True
        play_sound(self.eating_sound, volume=self.get_volume_from_player_pos(), pan=self.get_pan_from_player_pos())
        self.play_animation(*self.sitting_frames, looping=True)
        self.paralyze()
        self.eating_timer = 0

    def update_eating(self):
        if self.eating:
            if self.target_treat.picked_up or self.target_treat.decayed:
                self.stop_eating(success=False)
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
            if self.treats_eaten < (self.hunger-1):
                play_sound(self.swallow_sound, volume=self.get_volume_from_player_pos()*0.5, pan=self.get_pan_from_player_pos())
            self.target_treat.kill()
            self.treats_eaten += 1
        if self.treats_eaten >= self.hunger:
            play_sound(self.fed_sound, volume=self.get_volume_from_player_pos(), pan=self.get_pan_from_player_pos())
            self.paralyze()
            self.start_fade()
            self.player.give_xp(self.hunger)

        self.stop_animation()
        self.target_treat = None

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

    def update_movement_direction(self):
        if self.target_treat and not self.fleeing:
            self.face(self.target_treat.position)
        elif self.should_turn:
            self.randomize_velocity()
            self.random_movement_timer = 0

    def update_animation(self, delta_time):
        super().update_animation(delta_time)

    @property
    def should_sprint(self):
        return (self.target_treat is not None) or self.fleeing

    @property
    def should_meow(self):
        return self.meow_timer >= (self.meow_time+random.uniform(-self.meow_time*0.5, self.meow_time*3))

    def draw_debug(self):
        super().draw_debug()
        kitty_debug_text = arcade.Text(f"fleeing: {self.fleeing} eating: {self.eating}\neatingprogress: {round(self.eating_timer/self.eating_time,1)}\nfleeingprogress: {round(self.fleeing_timer/self.fleeing_time,1)}", start_x=self.center_x+self.width, start_y=self.center_y, color=arcade.color.BLACK, font_size=12, width=self.width, anchor_x="left", anchor_y="center", multiline=True)
        kitty_debug_text.draw()
