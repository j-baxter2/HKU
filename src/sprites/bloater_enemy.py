import arcade
import math
from src.sprites.enemy import BaseEnemy
from src.moves.move_radial_enemy import MoveEnemyBloat
from src.data.constants import DELTA_TIME
from pyglet.math import Vec2

class BloatingEnemy(BaseEnemy):
    def __init__(self, id: int, scene: arcade.Scene):
        self.scene = scene
        super().__init__(id, self.scene)
        self.slime_move = None

        self.treats = self.scene.get_sprite_list("Treat")
        self.target_treat = None
        self.treats_held = []
        self.treat_capacity = 4

        self.bloating = False
        self.bloating_color = arcade.color.ORANGE
        self.bloating_timer = 0
        self.bloating_time = 4

        self.vulnerable = False
        self.vulnerable_color = arcade.color.GOLD
        self.vulnerable_timer = 0
        self.vulnerable_time = 2

        self.holding_treat = False

    def setup(self):
        super().setup()
        self.slime_move = MoveEnemyBloat(id=9, scene=self.scene, origin_sprite=self)
        self.attack = self.slime_move.damage

    def update_while_alive(self):
        if not self.vulnerable and not self.bloating:
            self.locate_treat()
            self.handle_treat_collision()
        self.slime_move.on_update(DELTA_TIME)
        self.monitor_player_position()
        self.update_bloating()
        self.update_vulnerable()
        self.update_treats()

    def update_treats(self):
        self.treats = self.scene.get_sprite_list("Treat")
        for i, treat in enumerate(self.treats_held):
            treat.being_held = True
            offset = 16 * (i + 1)
            if self.bloating or self.vulnerable and not (self.player.fading or self.player.faded):
                vel = Vec2(self.player.center_x - self.center_x, self.player.center_y - self.center_y)
                angle = vel.heading
            else:
                self.velocity = Vec2(self.velocity[0], self.velocity[1])
                angle = self.velocity.heading
            treat.center_x = self.center_x - offset * math.cos(angle)
            treat.center_y = self.center_y - offset * math.sin(angle)

    def locate_treat(self):
        closest_treat = None
        min_distance = float('inf')

        for treat in self.treats:
            distance = arcade.get_distance_between_sprites(self, treat)
            if distance < self.follow_distance and not treat.being_held and not self.full:
                if distance < min_distance:
                    closest_treat = treat
                    min_distance = distance

        self.target_treat = closest_treat

    def handle_treat_collision(self):
        if self.target_treat:
            if arcade.check_for_collision(self, self.target_treat) and not self.full:
                self.grab_treat()

    def grab_treat(self):
        self.target_treat.being_held = True
        self.treats_held.append(self.target_treat)

    def drop_all_treats(self):
        for treat in self.treats_held[:]:
            treat.being_held = False
            self.treats_held.remove(treat)

    def update_movement_direction(self):
        if self.vulnerable:
            self.face_away(self.apparent_player_position())
        elif self.bloating and not (self.player.fading or self.player.faded):
            self.face(self.apparent_player_position())
        elif self.target_treat:
            self.face(self.target_treat.position)
        elif self.should_turn:
            self.randomize_velocity()
            self.random_movement_timer = 0

    def update_movement_speed(self):
        if self.should_stop:
            self.speed = 0
        elif self.vulnerable:
            self.speed = self.sprint_multiplier * self.base_speed
        elif self.bloating or self.target_treat:
            self.speed = (self.sprint_multiplier/2) * self.base_speed
        else:
            self.speed = self.base_speed

    def start_bloating(self):
        self.bloating = True
        self.bloating_timer = 0

    def update_bloating(self):
        if self.bloating:
            self.bloating_timer += DELTA_TIME
            self.oscillate_size()
            self.color = self.bloating_color
            if self.bloating_timer >= self.bloating_time:
                self.stop_bloating()

    def stop_bloating(self):
        self.bloating = False
        self.bloating_timer = 0
        self.slime_move.start()
        self.start_vulnerable()

    def start_vulnerable(self):
        self.vulnerable = True
        self.vulnerable_timer = 0

    def update_vulnerable(self):
        if self.vulnerable:
            self.vulnerable_timer += DELTA_TIME
            self.color = self.vulnerable_color
            if self.vulnerable_timer >= self.vulnerable_time:
                self.stop_vulnerable()

    def stop_vulnerable(self):
        self.vulnerable = False
        self.vulnerable_timer = 0

    def monitor_player_position(self):
        if arcade.get_distance_between_sprites(self, self.player) < 256 and not self.bloating and not self.vulnerable:
            self.start_bloating()

    def take_damage(self, amount: int):
        if self.vulnerable:
            return super().take_damage(amount)
        else:
            return

    def start_fade(self):
        self.drop_all_treats()
        super().start_fade()

    def oscillate_size(self):
        self.scale += 0.2 * math.sin(self.bloating_timer * 5*2*math.pi / self.bloating_time)

    @property
    def should_stop(self):
        return arcade.get_distance_between_sprites(self, self.player) < 64 and not self.vulnerable

    @property
    def full(self):
        return len(self.treats_held) >= self.treat_capacity

    def draw_debug(self):
        super().draw_debug()
        self.slime_move.draw_debug(0)
        debug_text = arcade.Text(f"Bloating: {self.bloating} {round(self.bloating_fraction*100,2)}%\nVulnerable: {self.vulnerable} {round(self.vulnerable_fraction*100,2)}%\nTreat: {len(self.treats_held)}", start_x=self.center_x, start_y=self.top, color=arcade.color.BLACK, font_size=12, anchor_x="center", anchor_y="bottom", multiline=True, width = 256)
        debug_text.draw()

    @property
    def bloating_fraction(self):
        return self.bloating_timer / self.bloating_time

    @property
    def vulnerable_fraction(self):
        return self.vulnerable_timer / self.vulnerable_time
