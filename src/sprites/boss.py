import arcade
import math
from src.sprites.enemy import BaseEnemy
from src.data.constants import DELTA_TIME
from src.moves.move_boss_horiz import MoveBossHoriz
from src.moves.move_boss_vert import MoveBossVert
from src.moves.move_boss_seek import MoveBossSeek


class Boss(BaseEnemy):
    def __init__(self, id: int, scene: arcade.Scene):
        self.scene = scene
        super().__init__(id, self.scene)
        self.horiz_move = None

        self.vert_move = None

        self.seek_move = None

        self.moves = []

        self.life_timer = 0

        self.vulnerable = False
        self.vulnerable_timer = 0
        self.vulnerable_time = 4

        self.player_found = False

    def setup(self):
        self.horiz_move = MoveBossHoriz(id=10, scene=self.scene, origin_sprite=self)
        self.vert_move = MoveBossVert(id=11, scene=self.scene, origin_sprite=self)
        self.seek_move = MoveBossSeek(id=12, scene=self.scene, origin_sprite=self)
        self.moves = [self.horiz_move, self.vert_move, self.seek_move]

        self.attack = self.horiz_move.damage
        super().setup()

    def update_while_alive(self):
        self.bob()
        for move in self.moves:
            move.on_update(DELTA_TIME)
        self.life_timer += DELTA_TIME
        self.update_player_found()

    def start_player_found(self):
        self.player_found = True
        self.horiz_move.start()

    def update_player_found(self):
        if not self.player_found and self.should_stop:
            self.start_player_found()


    def start_attacks(self):
        self.horiz_move.execute()

    def take_damage(self, amount: int):
        if self.vulnerable:
            return super().take_damage(amount)
        else:
            return

    def update_movement_direction(self):
        if self.should_chase:
            self.face(self.player.position)
        elif self.should_turn:
            self.randomize_velocity()
            self.random_movement_timer = 0

    def update_movement_speed(self):
        if self.should_stop:
            self.speed = 0
        elif self.should_chase:
            self.speed = self.player.speed
        else:
            self.speed = self.base_speed

    def bob(self):
        self.center_y += math.sin(self.life_timer*4)*0.5

    @property
    def should_chase(self):
        return arcade.get_distance_between_sprites(self, self.player) > self.follow_distance

    @property
    def should_stop(self):
        return arcade.get_distance_between_sprites(self, self.player) <= self.follow_distance

    def draw_debug(self):
        super().draw_debug()
        self.draw_hit_box()
        index = 0
        for move in self.moves:
            move.draw_debug(index)
            index += 1
