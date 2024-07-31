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

    def setup(self):
        super().setup()
        self.shoot_move = MoveEnemyShoot(id=6, scene=self.scene, origin_sprite=self)

    def update_while_alive(self):
        self.update_shooting()
        self.shoot_move.on_update(DELTA_TIME)
        self.color = arcade.color.RED

    def update_movement_direction(self):
        if self.in_range and not (self.player.fading or self.player.faded):
            self.face_player()
        elif self.should_turn:
            self.randomize_velocity()
            self.random_movement_timer = 0

    def update_shooting(self):
        if self.in_range and not self.shoot_move.refreshing:
            self.shoot_move.start()

    def draw_debug(self):
        super().draw_debug()
        self.shoot_move.draw_debug(0)
