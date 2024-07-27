import arcade
import json
import math
from src.sprites.moving_sprite import MovingSprite
from src.moves.move import Move
from src.data.constants import DELTA_TIME
from pyglet.math import Vec2

class Projectile(MovingSprite):
    def __init__(self, id: int, scene: arcade.Scene, origin_move: Move, start: tuple, target: tuple = (0,0), angle: float = 0, targetting_method: str = "tuple"):
        with open("resources/data/projectile.json", "r") as file:
            projectile_dict = json.load(file)
        self.projectile_data = projectile_dict[str(id)]
        self.scene = scene
        super().__init__(self.projectile_data)
        self.scene = scene
        self.origin_move = origin_move
        self.being = False
        self.being_time = self.projectile_data["being time"]
        self.being_timer = 0
        self.hit_sprites = None
        self.start_x = start[0]
        self.start_y = start[1]
        if targetting_method == "tuple":
            self.target_x = target[0]
            self.target_y = target[1]
        elif targetting_method == "angle":
            self.target_x = start[0] + math.sin(math.radians(angle))
            self.target_y = start[1] + math.cos(math.radians(angle))


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
        self.being = True
        self.play_animation(0, 1, looping=True)

    def update_activity(self):
        if self.being:
            self.being_timer += DELTA_TIME
            self.get_hit_sprites()
            if self.hit_sprites is not None:
                for sprite in self.hit_sprites:
                    print("executing damage sprite")
                    self.damage_sprite(sprite)
            if self.being_timer >= self.being_time:
                self.being = False
                self.start_fade()

    def get_hit_sprites(self):
        potential_hit_sprites = self.scene.get_sprite_list(self.origin_move.affects)
        potential_hit_sprites_alive = arcade.SpriteList()
        for sprite in potential_hit_sprites:
            if not (sprite.fading or sprite.faded):
                potential_hit_sprites_alive.append(sprite)
        hit_sprites = arcade.check_for_collision_with_list(self, potential_hit_sprites_alive)
        if len(hit_sprites) > 0:
            print("Sprites hit")
        self.hit_sprites = hit_sprites

    def damage_sprite(self, sprite):
        sprite.take_damage(self.origin_move.damage)
        if sprite.is_dead:
            self.origin_move.origin_sprite.give_xp(sprite.max_hp*sprite.attack)

    def update_movement_direction(self):
        arcade.get_angle_degrees(self.start_x, self.start_y, self.target_x, self.target_y)
        self.velocity = Vec2(self.target_x-self.start_x, self.target_y-self.start_y)

    def update_movement_speed(self):
        self.speed = self.base_speed

    def update_movement(self):
        super().update_movement()

    def draw_debug(self):
        super().draw_debug()
        kitty_debug_text = arcade.Text(f"being: {self.being}\ntimer:{round(self.being_timer/self.being_time,2)}", start_x=self.center_x+self.width, start_y=self.center_y, color=arcade.color.BLACK, font_size=12, width=self.width, anchor_x="left", anchor_y="center", multiline=True)
        kitty_debug_text.draw()
