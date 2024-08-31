import arcade
import math
from src.sprites.enemy import BaseEnemy
from src.moves.move_radial_enemy import MoveEnemyBloat
from src.data.constants import DELTA_TIME

class BloatingEnemy(BaseEnemy):
    def __init__(self, id: int, scene: arcade.Scene):
        self.scene = scene
        super().__init__(id, self.scene)
        self.slime_move = None
        self.bloating = True
        self.vulnerable = False
        self.bloating_timer = 0
        self.bloating_time = 4
        self.vulnerable_timer = 0

    def setup(self):
        super().setup()
        self.slime_move = MoveEnemyBloat(id=6, scene=self.scene, origin_sprite=self)
        self.attack = self.slime_move.damage

    def update_while_alive(self):
        self.slime_move.on_update(DELTA_TIME)
        self.monitor_player_position()
        self.update_bloating()

    def start_bloating(self):
        self.bloating = True
        self.bloating_timer = 0

    def update_bloating(self):
        if self.bloating:
            self.bloating_timer += DELTA_TIME
            self.oscillate_size()
            self.color = arcade.color.PURPLE_MOUNTAIN_MAJESTY
            if self.bloating_timer >= self.bloating_time:
                self.stop_bloating()

    def stop_bloating(self):
        self.bloating = False
        self.bloating_timer = 0

    def monitor_player_position(self):
        if arcade.get_distance_between_sprites(self, self.player) < 256 and not self.bloating:
            self.start_bloating()

    def take_damage(self, amount: int):
        if self.vulnerable:
            return super().take_damage(amount)
        else:
            return

    def oscillate_size(self):
        self.scale += 0.2 * math.sin(self.bloating_timer* 10*math.pi / self.bloating_time)

    def draw_debug(self):
        super().draw_debug()
        self.slime_move.draw_debug(0)
        debug_text = arcade.Text(f"Bloating: {self.bloating} {round(self.bloating_fraction*100,2)}%", start_x=self.center_x, start_y=self.top, color=arcade.color.BLACK, font_size=12, anchor_x="center", anchor_y="bottom", multiline=True, width = 256)
        debug_text.draw()

    @property
    def bloating_fraction(self):
        return self.bloating_timer / self.bloating_time
