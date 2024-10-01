import arcade
from src.sprites.living_sprite import LivingSprite
from src.sprites.projectile_specify import ProjectileSpecify
from src.moves.move import Move

class MoveEnemyBloat(Move):
    def __init__(self, id: int, scene: arcade.Scene, origin_sprite: LivingSprite):
        super().__init__(id, scene, origin_sprite)
        self.n_proj = 8

    def start(self):
        origin_pos_when_fired = self.origin_sprite.position
        for i in range(self.n_proj):
            self.projectile = ProjectileSpecify(id=0, scene=self.scene, origin_move=self, start=origin_pos_when_fired, angle=45*i, targetting_method="angle", range=512)
            self.scene.add_sprite("Projectile", self.projectile)
            self.projectile.start()

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
