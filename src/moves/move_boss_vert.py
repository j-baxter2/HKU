import arcade
import random
from src.sprites.living_sprite import LivingSprite
from src.sprites.projectile_specify import ProjectileSpecify
from src.moves.move import Move
from src.data.constants import DELTA_TIME, LINE_HEIGHT

class MoveBossVert(Move):
    def __init__(self, id: int, scene: arcade.Scene, origin_sprite: LivingSprite):
        super().__init__(id, scene, origin_sprite)
        self.n_proj = 16
        self.proj_fired = 0
        self.player_pos = None
        self.projectile = None
        self.first_shot_timer = 0

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
                self.fire("down")

            if 0 < self.proj_fired < self.n_proj:
                self.first_shot_timer += DELTA_TIME
                if self.first_shot_timer >= 0.5*(1 - (self.proj_fired/self.n_proj)) and self.proj_fired < self.n_proj:
                    if 1 <= self.proj_fired < 4 or 9 <= self.proj_fired < 12:
                        self.fire(random.choice(["down", "up"]))
                    else:
                        self.fire(random.choice(["left", "right"]))
                    self.first_shot_timer = 0

            if self.proj_fired >= self.n_proj:
                self.stop()

    def stop(self):
        self.active = False
        self.active_timer = 0
        self.first_shot_timer = 0
        self.proj_fired = 0

    def fire(self, direction):
        range_ = 1024
        offset = random.randint(-range_ // 8, range_ // 8)

        if direction == "down": # Down
            start = (
                self.get_target_pos_when_fired()[0] + offset,
                self.get_target_pos_when_fired()[1] + range_ // 2
            )

            target = (
                self.get_target_pos_when_fired()[0] + offset,
                self.get_target_pos_when_fired()[1] - range_ // 2
            )
        elif direction == "left": # Left
            start = (
                self.get_target_pos_when_fired()[0] + range_ // 2,
                self.get_target_pos_when_fired()[1] + offset
            )

            target = (
                self.get_target_pos_when_fired()[0] - range_ // 2,
                self.get_target_pos_when_fired()[1] + offset
            )
        elif direction == "up": # Up
            start = (
                self.get_target_pos_when_fired()[0] + offset,
                self.get_target_pos_when_fired()[1] - range_ // 2
            )

            target = (
                self.get_target_pos_when_fired()[0] + offset,
                self.get_target_pos_when_fired()[1] + range_ // 2
            )
        elif direction == "right": # Right
            start = (
                self.get_target_pos_when_fired()[0] - range_ // 2,
                self.get_target_pos_when_fired()[1] + offset
            )

            target = (
                self.get_target_pos_when_fired()[0] + range_ // 2,
                self.get_target_pos_when_fired()[1] + offset
            )

        self.projectile = ProjectileSpecify(
            id=2,
            scene=self.scene,
            origin_move=self,
            start=start,
            target=target,
            range=range_
        )

        self.scene.add_sprite("Projectile", self.projectile)
        self.projectile.start()
        self.proj_fired += 1

    def draw(self):
        arcade.draw_rectangle_filled(self.origin_sprite.position[0], self.origin_sprite.position[1], 32, 32, arcade.color.RED)

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
