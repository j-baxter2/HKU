import arcade
import math
from src.sprites.enemy import BaseEnemy
from src.data.constants import DELTA_TIME, LINE_HEIGHT
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

        self.attacking = False

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
        self.update_vulnerable()
        self.update_attacking()

    def start_player_found(self):
        self.player_found = True
        self.start_attacking()

    def update_player_found(self):
        if not self.player_found and self.should_stop:
            self.start_player_found()

    def start_vulnerable(self):
        self.vulnerable = True
        self.vulnerable_timer = 0

    def update_vulnerable(self):
        if self.vulnerable:
            self.vulnerable_timer += DELTA_TIME
            self.color = self.vulnerable_color
            if self.vulnerable_timer >= self.vulnerable_time:
                self.stop_vulnerable()
                self.start_attacking()

    def stop_vulnerable(self):
        self.vulnerable = False
        self.vulnerable_timer = 0
        self.color = arcade.color.WHITE

    def start_attacking(self):
        self.horiz_move.start()
        self.attacking = True

    def update_attacking(self):
        if self.attacking:
            if self.horiz_move.active == False:
                self.start_vulnerable()
                self.stop_attacking()

    def stop_attacking(self):
        self.attacking = False

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

    @property
    def vulnerable_color(self):
        sine_factor = 0.5 * math.sin(self.vulnerable_timer * 10 * math.pi / self.vulnerable_time)
        vulnerable_green = sine_factor * (127) + 127
        vulnerable_green = int(max(0, min(vulnerable_green, 255)))
        return (self.color[0], vulnerable_green, self.color[1])

    def draw_debug(self):
        super().draw_debug()
        self.draw_hit_box()
        index = 0
        for move in self.moves:
            move.draw_debug(index)
            index += 1
        start_x = self.left
        start_y = self.top-index*(LINE_HEIGHT*4)
        active_debug_text = arcade.Text(f"Vulnerable:{self.vulnerable}\n{self.vulnerable_timer:.1f}/{self.vulnerable_time}\nAttacking:{self.attacking}", start_x=start_x, start_y=start_y, color=arcade.color.BLACK, font_size=12, width=self.width, anchor_x="right", anchor_y="top", multiline=True)
        active_debug_text.draw()
