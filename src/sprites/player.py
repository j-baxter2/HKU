import arcade
from src.sprites.moving_sprite import MovingSprite
import json
from pyglet.math import Vec2
from src.utils.move import Move
from src.utils.sound import load_sound, play_sound
from src.data.constants import DELTA_TIME

class Player(MovingSprite):

    def __init__(self, id: int):
        with open("resources/data/player.json", "r") as file:
            player_dict = json.load(file)
        self.player_data = player_dict[str(id)]

        super().__init__(self.player_data)

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

        self.hp = self.max_hp
        self.stamina = self.max_stamina
        self.sprinting = False

        self.fading = False
        self.fade_timer = 0
        self.fade_time = 3

        self.footstep_sound = load_sound(self.footstep_name)
        self.sound_update_timer = 0
        self.sound_update_time = self.footstep_sound.get_length()

    def setup(self):
        super().setup()

    def update(self):
        super().update()

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

    def update_fade(self):
        self.fade_timer += DELTA_TIME
        opacity_decrease = 255 * (self.fade_timer / 2)
        self.alpha = max(255 - opacity_decrease, 0)
        if self.fade_timer >= self.fade_time:
            self.fading = False
            self.faded = True
            self.kill()

    def update_sound(self):
        self.update_walking_sound()

    def update_walking_sound(self):
        if self.stationary:
            self.sound_update_timer = 0
        else:
            self.sound_update_timer += DELTA_TIME

        if self.sound_update_timer >= self.sound_update_time:
            play_sound(self.footstep_sound)
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

    def debug_draw(self):
        self.draw_hit_box()
        for move in self.move_set:
            move.debug_draw()
        arcade.draw_text(f"JBH: {self.just_been_hit}", self.center_x, self.center_y+100, arcade.color.WHITE, 20)
        super().debug_draw()

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
