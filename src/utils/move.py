import arcade
from src.sprites.moving_sprite import MovingSprite

class Move:
    def __init__(self, name: str, scene: arcade.Scene):
        self.name = name
        self.scene = scene
        self.range = 200
        self.affects = "Kitty"
        self.active_time = 1
        self.active = False
        self.active_for = 0

    def start(self):
        self.active = True
        self.active_for = 0

    def on_update(self, delta_time: float):
        if self.active:
            self.active_for += delta_time
            if self.active_for > self.active_time:
                self.stop()

    def stop(self):
        self.active = False
        self.active_for = 0

    def execute(self, origin_sprite: MovingSprite):
        if self.executable:
            self.start()
            self.damage_affectees(origin_sprite)
        else:
            print(f"{self.name} not executable")

    def get_affectees(self, origin_sprite: MovingSprite):
        affectees = []
        potential_affectees = self.scene.get_sprite_list(self.affects)
        for potential_affectee in potential_affectees:
            if arcade.get_distance_between_sprites(origin_sprite, potential_affectee) < self.range:
                affectees.append(potential_affectee)
        return affectees

    def damage_affectees(self, origin_sprite: MovingSprite):
        affectees = self.get_affectees(origin_sprite)
        for affectee in affectees:
            affectee.take_damage(1)

    def draw(self, origin_sprite: MovingSprite):
        arcade.draw_circle_outline(origin_sprite.center_x, origin_sprite.center_y, self.range, arcade.color.RED, 5)
        for affectee in self.get_affectees(origin_sprite):
            affectee_x, affectee_y = affectee.center_x, affectee.center_y
            arcade.draw_line(origin_sprite.center_x, origin_sprite.center_y, affectee_x, affectee_y, arcade.color.RED, 5)

    def debug_draw(self, origin_sprite: MovingSprite):
        arcade.draw_text(f"{self.name}: {self.active}\n{round(self.active_for, 1)}/{self.active_time}", origin_sprite.center_x - 50, origin_sprite.center_y - 100, arcade.color.BLACK, 12)

    @property
    def executable(self):
        return not self.active
