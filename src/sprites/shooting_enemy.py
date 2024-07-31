import arcade
from src.sprites.enemy import BaseEnemy
from src.moves.move_enemy_shoot import MoveEnemyShoot
from pyglet.math import Vec2
import random
import math
import json
from src.data.constants import MAP_WIDTH, MAP_HEIGHT, DELTA_TIME

class ShootingEnemy(BaseEnemy):
    def __init__(self, id: int, scene: arcade.Scene):
        self.scene = scene
        super().__init__(id, self.scene)
        self.shoot_move = None
        self.fleeing = False
        self.fleeing_timer = 0
        self.fleeing_time = 0

    def setup(self):
        super().setup()
        self.shoot_move = MoveEnemyShoot(id=6, scene=self.scene, origin_sprite=self)
        self.fleeing_time = self.shoot_move.refresh_time

    def update_while_alive(self):
        self.update_shooting()
        self.update_monitor_player_proximity()
        self.update_fleeing()
        self.shoot_move.on_update(DELTA_TIME)
        self.color = arcade.color.RED

    def update_movement_direction(self):
        if self.in_range and self.fleeing:
            self.face_away_player()
        elif self.in_range and not (self.player.fading or self.player.faded) and not self.fleeing:
            self.face_player()
        elif self.should_turn:
            self.randomize_velocity()
            self.random_movement_timer = 0

    def update_movement_speed(self):
        if self.should_stop:
            self.speed = 0
        elif self.should_sprint:
            self.speed = self.sprint_multiplier * self.base_speed
        else:
            self.speed = self.base_speed

    def update_shooting(self):
        if self.in_range_to_shoot:
            self.shoot_move.start()

    def update_monitor_player_proximity(self):
        if self.player_too_close or self.just_been_hit:
            self.start_fleeing()

    def start_fleeing(self):
        self.fleeing = True
        self.fleeing_timer = 0
        #play scared sound

    def update_fleeing(self):
        if self.fleeing:
            self.fleeing_timer += DELTA_TIME
            if self.fleeing_timer >= self.fleeing_time:
                self.fleeing = False
                self.fleeing_timer = 0

    def face_away_player(self):
        self.velocity = Vec2(-(self.apparent_player_position[0] - self.center_x), -(self.apparent_player_position[1] - self.center_y))

    @property
    def player_too_close(self):
        return arcade.get_distance_between_sprites(self, self.player) < self.width*2

    @property
    def in_range_to_shoot(self):
        return arcade.get_distance_between_sprites(self, self.player) < self.shoot_move.range and not self.shoot_move.refreshing

    @property
    def should_sprint(self):
        return (self.in_range and self.shoot_move.refreshing)

    @property
    def should_stop(self):
        return arcade.get_distance_between_sprites(self, self.player) < self.shoot_move.range and not self.fleeing

    @property
    def fleeing_fraction(self):
        return self.fleeing_timer/self.fleeing_time

    @property
    def apparent_player_position(self):
        true_player_position = self.player.position
        distance = arcade.get_distance_between_sprites(self, self.player)
        apparent_player_position = (true_player_position[0] + random.uniform(-distance/2, distance/2), true_player_position[1] + random.uniform(-distance/2, distance/2))
        return apparent_player_position

    def draw_debug(self):
        super().draw_debug()
        self.shoot_move.draw_debug(0)
        debug_text = arcade.Text(f"Fleeing: {self.fleeing} {round(self.fleeing_fraction*100,2)}%", start_x=self.center_x, start_y=self.top, color=arcade.color.BLACK, font_size=12, anchor_x="center", anchor_y="bottom", multiline=True, width = 256)
        debug_text.draw()
