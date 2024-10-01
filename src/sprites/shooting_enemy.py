import arcade
from sprites.enemy import BaseEnemy
from moves.move_enemy_shoot import MoveEnemyShoot
from data.constants import DELTA_TIME

class ShootingEnemy(BaseEnemy):
    def __init__(self, id: int, scene: arcade.Scene):
        self.scene = scene
        super().__init__(id, self.scene)
        self.shoot_move = None
        self.fleeing = False
        self.fleeing_timer = 0
        self.fleeing_time = 0
        self.attack = 0

    def setup(self):
        super().setup()
        self.shoot_move = MoveEnemyShoot(id=6, scene=self.scene, origin_sprite=self)
        self.fleeing_time = self.shoot_move.refresh_time
        self.attack = self.shoot_move.damage

    def update_while_alive(self):
        self.update_shooting()
        self.update_monitor_player_proximity()
        self.update_fleeing()
        self.shoot_move.on_update(DELTA_TIME)
        self.color = arcade.color.RED

    def update_movement_direction(self):
        if self.in_range and self.fleeing:
            self.face_away(self.apparent_player_position())
        elif self.in_range and not (self.player.fading or self.player.faded) and not self.fleeing:
            self.face(self.apparent_player_position())
        elif self.should_turn:
            self.randomize_velocity()
            self.random_movement_timer = 0

    def update_movement_speed(self):
        if self.should_stop:
            self.speed = 0
        elif self.should_sprint:
            self.speed = self.sprint_multiplier * self.base_speed
        else:
            self.speed = self.base_speed

    def update_shooting(self):
        if self.in_range_to_shoot and self.player.is_alive:
            self.shoot_move.start()

    def update_monitor_player_proximity(self):
        if self.player_too_close or self.just_been_hit:
            self.start_fleeing()

    @property
    def player_too_close(self):
        return arcade.get_distance_between_sprites(self, self.player) < self.width*2

    @property
    def in_range_to_shoot(self):
        return arcade.get_distance_between_sprites(self, self.player) < self.shoot_move.range and not self.shoot_move.refreshing

    @property
    def should_sprint(self):
        return (self.in_range and self.shoot_move.refreshing)

    @property
    def should_stop(self):
        return arcade.get_distance_between_sprites(self, self.player) < self.shoot_move.range and not self.fleeing

    @property
    def fleeing_fraction(self):
        return self.fleeing_timer/self.fleeing_time

    def draw_debug(self):
        super().draw_debug()
        self.shoot_move.draw_debug(0)
        debug_text = arcade.Text(f"Fleeing: {self.fleeing} {round(self.fleeing_fraction*100,2)}%", start_x=self.center_x, start_y=self.top, color=arcade.color.BLACK, font_size=12, anchor_x="center", anchor_y="bottom", multiline=True, width = 256)
        debug_text.draw()
