import arcade
from src.sprites.living_sprite import LivingSprite
from src.sprites.projectile_specify import ProjectileSpecify
from src.moves.move import Move
from src.data.constants import DELTA_TIME, LINE_HEIGHT

class MoveBossHoriz(Move):
    def __init__(self, id: int, scene: arcade.Scene, origin_sprite: LivingSprite):
        super().__init__(id, scene, origin_sprite)
        self.proj_fired = 0
        self.proj_max = 8
        self.projectile = None

    def on_update(self, delta_time: float):
        self.update_activity()

    def start(self):
        self.active = True
        self.active_timer = 0

    def fire(self):
        range_ = 512
        horizontal_offset = range_ if self.proj_fired % 2 == 0 else -range_

        start = (
            self.get_target_pos_when_fired()[0] + horizontal_offset // 2,
            self.get_target_pos_when_fired()[1]
        )

        self.projectile = ProjectileSpecify(
            id=1,
            scene=self.scene,
            origin_move=self,
            start=start,
            target=self.get_target_pos_when_fired(),
            range=range_
        )

        self.scene.add_sprite("Projectile", self.projectile)
        self.projectile.start()
        self.proj_fired += 1

    def update_activity(self):
        if self.active:
            self.active_timer += DELTA_TIME

            if (self.projectile is None or not self.projectile.active) and arcade.get_distance_between_sprites(self.origin_sprite, self.origin_sprite.player) <= self.range and self.proj_fired < self.proj_max:
                self.fire()
            elif self.proj_fired >= self.proj_max:
                self.stop()

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

    def draw_debug(self, index: int):
        start_x = self.origin_sprite.right
        start_y = self.origin_sprite.top-index*(LINE_HEIGHT*4)
        active_debug_text = arcade.Text(f"{self.name} \nactive: {self.active}\nactiveprogress: {round(self.progress_fraction, 2)}\nactivetimer: {round(self.active_timer, 2)}", start_x=start_x, start_y=start_y, color=arcade.color.BLACK, font_size=12, width=self.origin_sprite.width, anchor_x="left", anchor_y="top", multiline=True)
        active_debug_text.draw()
