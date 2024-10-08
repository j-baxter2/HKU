import arcade
from src.sprites.living_sprite import LivingSprite
from src.sprites.treat import Treat
import json
import math
from pyglet.math import Vec2
from src.moves.move import Move
from src.moves.move_affect_all_in_range import AffectAllMove
from src.moves.move_target_arrowkey import TargetArrowKey
from src.moves.move_radial_fireball import RadialProjectile
from src.moves.move_custom_fire import MoveCustomFire
from src.moves.move_mouse_aim import MoveMouseAim
from src.moves.move_arrow_aim import MoveArrowAim

from src.utils.sound import load_sound, play_sound, FootstepSoundHandler
from src.data.constants import DELTA_TIME, MAP_WIDTH, MAP_HEIGHT, SOUND_EFFECT_VOL, LINE_HEIGHT

class Player(LivingSprite):
    def __init__(self, id: int, scene: arcade.Scene):
        with open("resources/data/player.json", "r") as file:
            player_dict = json.load(file)
        self.player_data = player_dict[str(id)]

        super().__init__(scene, self.player_data)

        self.scene = scene

        self.name = self.player_data["name"]

        self.max_stamina = self.player_data["stamina"]
        self.stamina_regen = self.player_data["stamina regen"]
        self.stamina_regen_bonus_stationary = self.player_data["stationary stamina bonus"]
        self.max_hp = self.player_data["hp"]
        self.hp = self.max_hp
        self.strength = self.player_data["strength"]
        self.stamina = self.max_stamina
        self.sprinting = False

        self.all_moves = []

        self.unlocked_moves = []

        self.equipped_moves = {
            "quick attack": None,
            "alt quick attack": None,
            "special": None,
            "alt special": None,
            "heal": None,
            "alt heal": None,
            "drop treat": None,
            "alt drop treat": None,
            "pickup treat": None,
            "alt pickup treat": None,
            "scare": None,
            "alt scare": None
        }

        self.active_moves = []
        self.charging_moves = []
        self.refreshing_moves = []

        self.xp = 0
        self.ranking_data = None
        self.current_rank = 0

        self.treat_amount = 0
        self.treat_sprite_list = None

        self.picking_up_treat = False
        #footstepsounds
        self.footstep_sounds = {}
        self.footstep_sounds["grass"] = load_sound("grass_step", source="hku")
        self.footstep_sounds["sand"] = load_sound("sand_step", source="hku")
        self.footstep_sounds["water"] = load_sound("water_step", source="hku")
        self.footstep_sounds["wood"] = load_sound("wood_step", source="hku")
        self.cur_footstep_key = "grass"
        self.footstep_handler = FootstepSoundHandler(self)
        self.drop_treat_sound = load_sound("hit5")
        self.pick_up_treat_sound = load_sound("coin5")
        self.no_treat_sound = load_sound("error1")

        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.sprint_pressed = False
        self.alt_pressed = False

        self.able_to_move = False

        self.fading_in = True
        self.fade_in_timer = 0
        self.fade_in_time = 2

        self.attack = 0

        self.inside = False

        with open("resources/maps/terrain_mapping.json", "r") as file:
            self.terrain_mapping = json.load(file)

    def setup(self):
        self.treat_sprite_list = self.scene.get_sprite_list("Treat")
        self.load_ranking_data()
        basic_attack = AffectAllMove(0, self.scene, self)
        basic_heal = AffectAllMove(1, self.scene, self)
        shock = AffectAllMove(2, self.scene, self)
        scare = AffectAllMove(3, self.scene, self)
        ranged = TargetArrowKey(4, self.scene, self)
        radial = RadialProjectile(5, self.scene, self)
        custom_fire = MoveCustomFire(8, self.scene, self)
        arrow_aim = MoveArrowAim(7, self.scene, self)
        self.unlock_moves(basic_attack)
        self.unlock_moves(basic_heal)
        self.unlock_moves(scare)
        self.unlock_moves(radial)
        self.unlock_moves(custom_fire)
        self.unlock_moves(arrow_aim)
        self.equip_move("quick attack", basic_attack)
        self.equip_move("special", arrow_aim)

    def update(self):
        super().update()
        if self.fading:
            self.update_fade()
        elif self.able_to_move:
            self.update_movement()
        if not self.at_max_rank:
            self.update_level_up()
        if self.fading_in:
            self.update_fade_in()
        self.update_terrain()
        self.update_from_terrain()
        self.update_animation()
        self.update_sound()
        self.update_sprinting_flag()
        self.update_stamina(DELTA_TIME)
        self.update_moves()
        self.update_treat_list()
        self.update_treat_pickup()

    def draw(self):
        super().draw()

    def update_fade_in(self):
        if self.fading_in:
            self.fade_in_timer+=DELTA_TIME
            self.alpha = min(self.fade_in_fraction * 255, 255)
            if self.fade_in_timer >= self.fade_in_time:
                self.fading_in = False
                self.able_to_move = True
                self.fade_in_timer = 0

    def load_ranking_data(self):
        with open("resources/data/player_levelling.json", "r") as file:
            ranking_data = json.load(file)
        self.ranking_data = ranking_data

    def update_level_up(self):
        next_rank_data = self.ranking_data[str(self.current_rank+1)]
        if self.xp > next_rank_data["xp"]:
            self.current_rank += 1
            current_rank_data = next_rank_data
            self.max_hp += current_rank_data["hp"]
            self.hp = self.max_hp
            self.strength += current_rank_data["strength"]
            self.max_stamina += current_rank_data["stamina"]
            self.stamina = self.max_stamina
            if current_rank_data["unlock"] is not None:
                for move in self.all_moves:
                    if move.name in current_rank_data["unlock"]:
                        self.unlock_moves(move)


    def get_xp_to_next_level(self):
        return self.ranking_data[str(self.current_rank+1)]["xp"] - self.xp

    def get_xp_from_previous_level(self):
        return self.xp - self.ranking_data[str(self.current_rank)]["xp"]

    def get_xp_fraction(self):
        if self.get_xp_to_next_level() == 0:
            return 1
        else:
            return min(self.get_xp_from_previous_level() / self.get_xp_to_next_level(), 1)

    def update_terrain(self):
        floor = self.scene.get_sprite_list("Floor")
        hit_tiles = arcade.check_for_collision_with_list(self, floor)
        if hit_tiles:
            current_tile = hit_tiles[0]
            tile_id = current_tile.properties['tile_id']
            terrain = self.terrain_mapping[str(tile_id)]
            self.walking_on = terrain

    def update_from_terrain(self):
        self.speed_multiplier = 1
        self.current_movement_frames = self.walk_cycle_frames
        if self.walking_on == "water":
            self.speed_multiplier = 0.3
            self.current_movement_frames = self.swim_cycle_frames
            self.cur_footstep_key = "water"
        elif self.walking_on == "sand":
            self.cur_footstep_key = "sand"
        elif self.walking_on == "stone":
            self.cur_footstep_key = "sand"
        elif self.walking_on == "wood":
            self.cur_footstep_key = "wood"
        elif self.walking_on == "grass":
            self.cur_footstep_key = "grass"



    def update_stamina(self, delta_time):
        if self.sprinting:
            self.stamina -= 1
        elif self.stationary:
            self.stamina += (self.stamina_regen + self.stamina_regen_bonus_stationary) * delta_time
        else:
            self.stamina += self.stamina_regen * delta_time

        self.stamina = max(0, min(self.stamina, self.max_stamina))

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

    def update_moves(self):
        for move in self.unlocked_moves:
            move.on_update(DELTA_TIME)
        if self.inside:
            if not hasattr(self, '_original_do_move'):
                self._original_do_move = self.do_move
            self.do_move = lambda dummy: None
        else:
            if hasattr(self, '_original_do_move'):
                self.do_move = self._original_do_move
                del self._original_do_move

    def update_sprinting_flag(self):
        self.sprinting = (self.sprint_pressed and not self.stationary)

    def update_animation(self):
        if not self.current_animation:
            if self.up_pressed:
                self.start_walk_cycle('up')
            elif self.down_pressed:
                self.start_walk_cycle('down')
            elif self.left_pressed:
                self.start_walk_cycle('left')
            elif self.right_pressed:
                self.start_walk_cycle('right')
        self.advance_animation()

    def drop_treat(self):
        treat = Treat("resources/spritesheets/treat.png", 4)
        treat.center_x = self.left
        treat.center_y = self.center_y
        self.scene.add_sprite("Treat", treat)
        play_sound(self.drop_treat_sound, volume=SOUND_EFFECT_VOL)
        self.treat_amount -= 1

    def update_treat_list(self):
        self.treat_sprite_list = self.scene.get_sprite_list("Treat")

    def update_treat_pickup(self):
        treats = arcade.check_for_collision_with_list(self, self.treat_sprite_list)
        for treat in treats:
            if treat.decayed:
                self.pick_up_treat(treat)
            elif not treat.decayed and self.picking_up_treat:
                self.pick_up_treat(treat)


    def pick_up_treat(self, treat):
        play_sound(self.pick_up_treat_sound, volume=SOUND_EFFECT_VOL)
        self.treat_amount += 1
        treat.picked_up = True
        treat.kill()

    def update_sound(self):
        self.update_walking_sound()

    def update_walking_sound(self):
        self.footstep_handler.update_sound()

    def give_xp(self, amount: int):
        self.xp += amount

    def get_integer_position(self):
        return (int(self.center_x), int(self.center_y))

    def unlock_moves(self, move):
        if move not in self.unlocked_moves:
            self.unlocked_moves.append(move)

    def equip_move(self, slot, move):
        if move in self.unlocked_moves:
            if slot[0:4] == "alt ":
                primary = slot[4:]
                if self.equipped_moves[primary] == move:
                    self.equipped_moves[primary] = None
                    print("unequipped move from primary slot")
            self.equipped_moves[slot] = move

    def do_move(self, move):
        if move.type == "basic":
            move.execute()
        elif move.type == "charge" or move.type == "charge and release":
            move.start_charge()

    def stop_move(self, move):
        if move.type == "basic":
            pass
        elif move.type == "charge":
            move.stop_charge()
        elif move.type == "charge and release":
            move.fire()

    def change_target(self, direction: str):
        for slot, move in self.equipped_moves.items():
            if (hasattr(move, "choosing_target") and move.choosing_target):
                move.change_target(direction)

    @property
    def doing_move(self):
        for move in self.unlocked_moves:
            if move.active:
                return True
        return False

    @property
    def choosing_target(self):
        for move in self.unlocked_moves:
            if hasattr(move, "choosing_target") and move.choosing_target:
                return True
        return False

    @property
    def charging_move(self):
        for move in self.unlocked_moves:
            if move.charging:
                return True
        return False

    @property
    def charged_move(self):
        for move in self.unlocked_moves:
            if move.charged:
                return True
        return False

    @property
    def refreshing_move(self):
        for move in self.unlocked_moves:
            if move.refreshing:
                return True
        return False

    def get_refreshing_moves(self):
        refreshing_moves = []
        for move in self.unlocked_moves:
            if move.refreshing:
                refreshing_moves.append(move)
        return refreshing_moves

    def get_active_moves(self):
        active_moves = []
        for move in self.unlocked_moves:
            if move.active:
                active_moves.append(move)
        return active_moves

    def get_charge_moves(self):
        charge_moves = []
        for move in self.unlocked_moves:
            if move.charging or (move.type == "charge and release" and move.charged):
                charge_moves.append(move)
        return charge_moves

    @property
    def has_treats(self):
        return self.treat_amount > 0

    @property
    def should_sprint(self):
        return self.stamina > 0 and self.sprint_pressed

    @property
    def at_max_rank(self):
        return self.current_rank >= len(self.ranking_data) - 1

    @property
    def fade_in_fraction(self):
        return self.fade_in_timer/self.fade_in_time

    @property
    def in_battle(self):
        tuple = arcade.get_closest_sprite(self, self.scene.get_sprite_list("Enemy"))
        if tuple is not None:
            distance = tuple[1]
            return distance <= 1024 or self.just_been_hit
        else:
            return False

    def draw_debug(self):
        index = 0
        for slot, move in self.equipped_moves.items():
            if move:
                move.draw_debug(index)
                index += 1
        xp_text = arcade.Text(f"xp: {self.xp}\nIB: {self.in_battle}", start_x=self.center_x, start_y=self.top+LINE_HEIGHT, color=arcade.color.WHITE, font_size=20, anchor_x="center", anchor_y="bottom")
        xp_text.draw()
        inside_text = arcade.Text(f"inside: {self.inside}", start_x=self.center_x, start_y=self.top+2*LINE_HEIGHT, color=arcade.color.WHITE, font_size=20, anchor_x="center", anchor_y="bottom")
        inside_text.draw()
        super().draw_debug()
