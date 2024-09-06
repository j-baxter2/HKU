import arcade
import math
from src.sprites.enemy import BaseEnemy
from src.data.constants import DELTA_TIME, LINE_HEIGHT
from src.moves.move_boss_horiz import MoveBossHoriz
from src.moves.move_boss_vert import MoveBossVert
from src.moves.move_boss_seek import MoveBossSeek
from src.utils.sound import load_sound, play_sound


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
        self.attacking_timer = 0

        self.player_found = False

        self.move_index = 0

        self.vulnerable_sound = load_sound("norris_vulnerable", source="hku")
        self.attacking_sound = load_sound("norris_attack", source="hku")
        self.attacking_player = None
        self.hit_sound = load_sound("norris_hit", source="hku")

    def setup(self):
        super().setup()
        self.horiz_move = MoveBossHoriz(id=10, scene=self.scene, origin_sprite=self)
        self.vert_move = MoveBossVert(id=11, scene=self.scene, origin_sprite=self)
        self.seek_move = MoveBossSeek(id=12, scene=self.scene, origin_sprite=self)
        self.moves = [self.horiz_move, self.vert_move, self.seek_move]

        self.attack = self.horiz_move.damage
        self.set_texture(0)

    def update_while_alive(self):
        self.bob()
        for move in self.moves:
            move.on_update(DELTA_TIME)
        self.life_timer += DELTA_TIME
        self.update_player_found()
        self.update_vulnerable()
        self.update_attacking()

    def update_animation(self, delta_time):
        return

    def start_player_found(self):
        self.player_found = True
        self.start_attacking()

    def update_player_found(self):
        if not self.player_found and self.should_stop:
            self.start_player_found()

    def start_vulnerable(self):
        self.vulnerable = True
        self.set_texture(0)
        self.vulnerable_sound.play(volume=self.get_volume_from_player_pos(), pan=self.get_pan_from_player_pos())
        self.vulnerable_timer = 0

    def update_vulnerable(self):
        if self.vulnerable:
            self.vulnerable_timer += DELTA_TIME
            self.color = self.vulnerable_color
            self.update_vulnerable_animation()
            if self.vulnerable_timer >= self.vulnerable_time:
                self.stop_vulnerable()
                self.start_attacking()

    def update_vulnerable_animation(self):
        texture_changes = [
            (0.5, 1),
            (1.0, 0),
            (1.5, 1),
            (2.0, 0),
            (2.5, 1),
            (3.0, 0),
            (3.5, 1)
        ]

        for interval, texture_index in texture_changes:
            if self.vulnerable_timer >= interval and self.texture != self.textures[texture_index]:
                self.set_texture(texture_index)

    def stop_vulnerable(self):
        self.vulnerable = False
        self.vulnerable_timer = 0
        self.color = arcade.color.WHITE

    def start_attacking(self):
        self.attacking = True
        self.set_texture(2)
        self.attacking_player = self.attacking_sound.play(volume=self.get_volume_from_player_pos(), pan=self.get_pan_from_player_pos())
        self.move_index = 0
        self.attacking_timer = 0

    def update_attacking(self):
        if self.attacking:
            self.attacking_timer += DELTA_TIME
            self.update_attacking_animation()
            if self.horiz_move.active == False and self.move_index == 0:
                self.horiz_move.start()
                self.move_index = 1
            elif self.horiz_move.active == False and self.move_index == 1:
                self.vert_move.start()
                self.move_index = 2
            elif self.vert_move.active == False and self.move_index == 2:
                self.start_vulnerable()
                self.stop_attacking()
            elif self.player.is_dead:
                self.stop_attacking(player_killed = True)

    def update_attacking_animation(self):
        if self.player.just_been_hit:
            if self.player.just_been_hit_timer < 0.02 and self.texture == self.textures[2]:
                self.set_texture(3)
                if not self.attacking_player.playing:
                    self.hit_sound.play(volume=self.get_volume_from_player_pos(), pan=self.get_pan_from_player_pos())
            if self.player.just_been_hit_timer >= 0.02 and self.texture == self.textures[3]:
                self.set_texture(4)
        else:
            self.set_texture(2)

    def stop_attacking(self, player_killed = False):
        self.attacking = False
        self.attacking_timer = 0
        if player_killed:
            pass
            #play some victory sound

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

    def get_active_moves(self):
        active_moves = []
        for move in self.moves:
            if move.active:
                active_moves.append(move)
        return active_moves

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
        active_debug_text = arcade.Text(f"Vulnerable:{self.vulnerable}\n{self.vulnerable_timer:.1f}/{self.vulnerable_time}\nAttacking:{self.attacking}\nTexture:{self.cur_texture_index}", start_x=start_x, start_y=start_y, color=arcade.color.BLACK, font_size=12, width=self.width, anchor_x="right", anchor_y="top", multiline=True)
        active_debug_text.draw()
