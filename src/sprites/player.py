import arcade
from src.sprites.moving_sprite import MovingSprite
from src.sprites.treat import Treat
import json
from pyglet.math import Vec2
from src.utils.move import Move
from src.utils.sound import load_sound, play_sound
from src.data.constants import DELTA_TIME, MAP_WIDTH, MAP_HEIGHT

class Player(MovingSprite):

    def __init__(self, id: int, scene: arcade.Scene):
        with open("resources/data/player.json", "r") as file:
            player_dict = json.load(file)
        self.player_data = player_dict[str(id)]

        super().__init__(self.player_data)

        self.scene = scene

        self.name = self.player_data["name"]

        self.sprint_multiplier = self.player_data["sprint multiplier"]
        self.max_stamina = self.player_data["stamina"]
        self.stamina_regen = self.player_data["stamina regen"]
        self.stamina_regen_bonus_stationary = self.player_data["stationary stamina bonus"]
        self.footstep_name = self.player_data["footstep name"]

        self.move_set = []

        self.active_moves = []
        self.charging_moves = []
        self.refreshing_moves = []

        self.xp = 0

        self.max_hp = self.player_data["hp"]
        self.hp = self.max_hp
        self.stamina = self.max_stamina
        self.sprinting = False

        self.footstep_sound = load_sound(self.footstep_name)
        self.sound_update_timer = 0
        self.sound_update_time = self.footstep_sound.get_length()

        self.treat_amount = 0
        self.treat_sprite_list = arcade.SpriteList()

        self.picking_up_treat = False

        self.drop_treat_sound = load_sound("upgrade1")
        self.no_treat_sound = load_sound("error1")

        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.sprint_pressed = False

    def setup(self):
        super().setup()

    def update(self):
        super().update()
        if self.fading:
            self.update_fade()
        elif self.able_to_move:
            self.update_movement()
        self.update_sound()
        self.update_animation()
        self.update_sprinting_flag()
        self.update_stamina(DELTA_TIME)
        self.update_moves()
        self.update_treat_pickup()

    def draw(self):
        super().draw()

    def update_stamina(self, delta_time):
        if self.sprinting:
            self.stamina -= 1
        elif self.stationary:
            self.stamina += (self.stamina_regen + self.stamina_regen_bonus_stationary) * delta_time
        else:
            self.stamina += self.stamina_regen * delta_time

        self.stamina = max(0, min(self.stamina, self.max_stamina))

    def update_movement(self):
        self.update_movement_direction()
        self.update_movement_speed()
        self.velocity = [self.velocity.x, self.velocity.y]
        self.center_x = max(0, min(self.center_x, MAP_WIDTH))
        self.center_y = max(0, min(self.center_y, MAP_HEIGHT))

    def update_movement_direction(self):
        self.velocity = Vec2(0, 0)
        if self.up_pressed:
            self.velocity += Vec2(0, 1)
        if self.down_pressed:
            self.velocity -= Vec2(0, 1)
        if self.left_pressed:
            self.velocity -= Vec2(1, 0)
        if self.right_pressed:
            self.velocity += Vec2(1, 0)
        self.velocity = self.velocity.normalize()

    def update_movement_speed(self):
        if self.stamina > 0:
            if self.sprint_pressed:
                self.speed = self.base_speed * self.sprint_multiplier
            else:
                self.speed = self.base_speed
        else:
            self.speed = self.base_speed
        self.velocity = self.velocity.scale(self.speed)

    def update_moves(self):
        for move in self.move_set:
            move.on_update(DELTA_TIME)

    def update_sprinting_flag(self):
        self.sprinting = (self.sprint_pressed and not self.stationary)

    def update_animation(self):
        if not self.current_walk_cycle:
            if self.up_pressed:
                self.start_walk_cycle('up')
            elif self.down_pressed:
                self.start_walk_cycle('down')
            elif self.left_pressed:
                self.start_walk_cycle('left')
            elif self.right_pressed:
                self.start_walk_cycle('right')
        self.advance_walk_cycle()

    def drop_treat(self):
        treat = Treat("resources/textures/map_tiles/default_apple.png", 1)
        treat.center_x = self.center_x
        treat.center_y = self.center_y
        self.treat_sprite_list.append(treat)
        self.scene.add_sprite_list(name="Treat", sprite_list=self.treat_sprite_list)

        play_sound(self.drop_treat_sound)
        self.treat_amount -= 1

    def update_treat_pickup(self):
        if self.picking_up_treat:
            treats = arcade.check_for_collision_with_list(self, self.treat_sprite_list)
            for treat in treats:
                self.treat_amount += 1
                treat.picked_up = True
                treat.kill()

    def update_sound(self):
        self.update_walking_sound()

    def update_walking_sound(self):
        if self.stationary:
            self.sound_update_timer = 0
        else:
            self.sound_update_timer += DELTA_TIME

        if self.sound_update_timer >= self.sound_update_time:
            play_sound(self.footstep_sound, volume=0.01)
            self.sound_update_timer = 0

    def get_integer_position(self):
        return (int(self.center_x), int(self.center_y))

    def add_move(self, move):
        self.move_set.append(move)

    def do_move(self, move_name: str):
        for move in self.move_set:
            if move.name == move_name and move.executable:
                move.execute()

    def start_charging_move(self, move_name: str):
        for move in self.move_set:
            if move.name == move_name:
                move.start_charge()

    def stop_charging_move(self, move_name: str):
        for move in self.move_set:
            if move.name == move_name:
                move.stop_charge()

    @property
    def doing_move(self):
        for move in self.move_set:
            if move.active:
                return True
        return False

    @property
    def charging_move(self):
        for move in self.move_set:
            if move.charging:
                return True
        return False

    @property
    def refreshing_move(self):
        for move in self.move_set:
            if move.refreshing:
                return True
        return False

    def get_refreshing_moves(self):
        refreshing_moves = []
        for move in self.move_set:
            if move.refreshing:
                refreshing_moves.append(move)
        return refreshing_moves

    def get_active_moves(self):
        active_moves = []
        for move in self.move_set:
            if move.active:
                active_moves.append(move)
        return active_moves

    def get_charging_moves(self):
        charging_moves = []
        for move in self.move_set:
            if move.charging:
                charging_moves.append(move)
        return charging_moves

    @property
    def has_treats(self):
        return self.treat_amount > 0

    def debug_draw(self):
        for move in self.move_set:
            move.debug_draw()
        arcade.draw_text(f"JBH: {self.just_been_hit}", self.center_x, self.center_y+100, arcade.color.WHITE, 20)
        super().debug_draw()
