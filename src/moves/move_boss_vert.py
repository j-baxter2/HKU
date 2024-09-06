import arcade
from src.sprites.living_sprite import LivingSprite
from src.sprites.projectile_specify import ProjectileSpecify
from src.moves.move import Move
from src.data.constants import DELTA_TIME, LINE_HEIGHT

class MoveBossVert(Move):
    def __init__(self, id: int, scene: arcade.Scene, origin_sprite: LivingSprite):
        super().__init__(id, scene, origin_sprite)
        self.n_proj = 8

    def start(self):
        self.active = True
        self.active_timer = 0

    def update_activity(self):
        if self.active:
            self.active_timer += DELTA_TIME
            if self.active_timer > self.active_time:
                self.stop()

    def stop(self):
        self.active = False
        self.active_timer = 0

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
