import arcade
import json
import math
from sprites.moving_sprite import MovingSprite
from moves.move import Move
from data.constants import DELTA_TIME, MAP_WIDTH, MAP_HEIGHT
from pyglet.math import Vec2

class ProjectileSeek(MovingSprite):
    def __init__(self, id: int, scene: arcade.Scene, origin_move: Move, start: tuple, target: tuple = (0,0), angle: float = 0, targetting_method: str = "tuple"):
        with open("resources/data/projectile.json", "r") as file:
            projectile_dict = json.load(file)
        self.projectile_data = projectile_dict[str(id)]
        self.scene = scene
        super().__init__(self.projectile_data)
        self.scene = scene
        self.origin_move = origin_move
        self.active = False
        self.active_time = 10
        self.active_timer = 0
        self.hit_sprites = None
        self.start_x = start[0]
        self.start_y = start[1]
        if targetting_method == "tuple":
            self.target_x = target[0]
            self.target_y = target[1]
        elif targetting_method == "angle":
            self.target_x = start[0] + math.sin(math.radians(angle))
            self.target_y = start[1] + math.cos(math.radians(angle))
        self.n_turns = 0
        self.max_turns = 16

    def update(self):
        self.update_movement()
        self.update_activity()
        self.update_animation()
        super().update()

    def start(self):
        angle = arcade.get_angle_degrees(self.start_x, self.start_y, self.target_x, self.target_y)
        self.angle -= angle
        self.center_x = self.start_x
        self.center_y = self.start_y
        self.active = True
        self.face()
        self.play_animation(0, 1, looping=True)

    def update_movement(self):
        if self.active:
            if self.active_timer >= (self.n_turns/self.max_turns)*self.active_time and self.n_turns < self.active_time % self.max_turns:
                self.n_turns += 1
                self.face()
                print("projectile turning")
            super().update_movement()

    def update_activity(self):
        if self.active:
            self.active_timer += DELTA_TIME
            self.angle -= 1
            self.handle_boss_collision()
            self.get_hit_sprites()
            if self.hit_sprites is not None:
                for sprite in self.hit_sprites:
                    self.damage_sprite(sprite)
            if self.active_timer >= self.active_time:
                self.active = False
                self.kill()

    def face(self):
        player = self.scene.get_sprite_list("Player")[0]
        if player is not None:
            super().face(player.position)

    def get_hit_sprites(self):
        potential_hit_sprites = self.scene.get_sprite_list(self.origin_move.affects)
        potential_hit_sprites_alive = arcade.SpriteList()
        for sprite in potential_hit_sprites:
            if not (sprite.fading or sprite.faded):
                potential_hit_sprites_alive.append(sprite)
        hit_sprites = arcade.check_for_collision_with_list(self, potential_hit_sprites_alive)
        self.hit_sprites = hit_sprites

    def damage_sprite(self, sprite):
        if not sprite.just_been_hit:
            sprite.take_damage(self.origin_move.damage)
            if sprite.is_dead:
                self.origin_move.origin_sprite.give_xp(sprite.max_hp*sprite.attack)

    def handle_boss_collision(self):
        if self.active_timer >= 1:
            boss = self.scene.get_sprite_list("Enemy")[0]
            if arcade.check_for_collision(self, boss):
                print("projectile hit boss")
                self.origin_move.stop()
                self.kill()

    def update_movement_direction(self):
        pass

    def handle_out_of_bounds(self):
        if self.center_x < 0 or self.center_x > MAP_WIDTH:
            self.kill()
        elif self.center_y < 0 or self.center_y > MAP_HEIGHT:
            self.kill()

    def draw_debug(self):
        super().draw_debug()
        kitty_debug_text = arcade.Text(f"active: {self.active}\ntimer:{round(self.active_timer/self.active_time,2)}", start_x=self.center_x+self.width, start_y=self.center_y, color=arcade.color.BLACK, font_size=12, width=self.width, anchor_x="left", anchor_y="center", multiline=True)
        kitty_debug_text.draw()