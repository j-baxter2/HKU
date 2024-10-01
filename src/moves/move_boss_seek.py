import arcade
import random
import math
from sprites.living_sprite import LivingSprite
from sprites.projectile_seek import ProjectileSeek
from moves.move import Move
from data.constants import DELTA_TIME, LINE_HEIGHT

class MoveBossSeek(Move):
    def __init__(self, id: int, scene: arcade.Scene, origin_sprite: LivingSprite):
        super().__init__(id, scene, origin_sprite)
        self.n_proj = 4
        self.proj_fired = 0
        self.player_pos = None
        self.projectile = None
        self.first_shot_timer = 0
        self.first_shot_time = 4

    def on_update(self, delta_time: float):
        self.update_activity()

    def start(self):
        self.active = True
        self.active_timer = 0
        self.first_shot_timer = 0  # Reset the timer when the move starts

    def update_activity(self):
        if self.active:
            self.active_timer += DELTA_TIME
            if self.active_timer >= 1 and self.proj_fired == 0:
                self.fire()

            if 0 < self.proj_fired < self.n_proj:
                self.first_shot_timer += DELTA_TIME
                if self.first_shot_timer >= self.first_shot_time and self.proj_fired < self.n_proj:
                    self.fire()
                    self.first_shot_timer = 0

            if self.proj_fired >= self.n_proj:
                self.stop()

    def stop(self):
        self.active = False
        self.active_timer = 0
        self.first_shot_timer = 0
        self.proj_fired = 0

    def fire(self):
        start = self.origin_sprite.position

        target_pos = self.get_target_pos_when_fired()
        if target_pos is None:
            self.stop()
            return

        target = (target_pos[0], target_pos[1])

        self.projectile = ProjectileSeek(
            id=3,
            scene=self.scene,
            origin_move=self,
            start=start,
            target=target,
            targetting_method="tuple"
        )

        self.scene.add_sprite("Projectile", self.projectile)
        self.projectile.start()
        self.projectile.center_x = self.origin_sprite.center_x
        self.projectile.center_y = self.origin_sprite.top
        self.proj_fired += 1

    def draw(self):
        arcade.draw_rectangle_filled(self.origin_sprite.position[0], self.origin_sprite.position[1], 32, 32, arcade.color.YELLOW)

    def get_target_pos_when_fired(self):
        player_list = self.scene.get_sprite_list("Player")
        if len(player_list) > 0:
            player = self.scene.get_sprite_list("Player")[0]
            return player.position
        else:
            return

    def execute(self):
        if self.executable and len(self.scene.get_sprite_list("Player") > 0):
            self.start()
