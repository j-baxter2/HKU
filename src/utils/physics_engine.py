from typing import Iterable, List, Optional, Union
import arcade
import math
from arcade import (Sprite, SpriteList, check_for_collision,
                    check_for_collision_with_lists, get_distance)
from pyglet.math import Vec2

def _circular_check(player: Sprite, walls: List[SpriteList]):
    """
    This is a horrible kludge to 'guess' our way out of a collision
    Returns:

    """
    original_x = player.center_x
    original_y = player.center_y

    vary = 1
    while True:
        try_list = [[original_x, original_y + vary],
                    [original_x, original_y - vary],
                    [original_x + vary, original_y],
                    [original_x - vary, original_y],
                    [original_x + vary, original_y + vary],
                    [original_x + vary, original_y - vary],
                    [original_x - vary, original_y + vary],
                    [original_x - vary, original_y - vary]
                    ]

        for my_item in try_list:
            x, y = my_item
            player.center_x = x
            player.center_y = y
            check_hit_list = check_for_collision_with_lists(player, walls)
            # print(f"Vary {vary} ({self.player_sprite.center_x} {self.player_sprite.center_y}) "
            #       f"= {len(check_hit_list)}")
            if len(check_hit_list) == 0:
                return
        vary *= 2


def _move_sprite(moving_sprite: Sprite, walls: List[SpriteList], ramp_up: bool) -> List[Sprite]:

    # See if we are starting this turn with a sprite already colliding with us.
    if len(check_for_collision_with_lists(moving_sprite, walls)) > 0:
        _circular_check(moving_sprite, walls)

    original_x = moving_sprite.center_x
    original_y = moving_sprite.center_y
    original_angle = moving_sprite.angle

    # --- Rotate
    rotating_hit_list = []
    if moving_sprite.change_angle:

        # Rotate
        moving_sprite.angle += moving_sprite.change_angle

        # Resolve collisions caused by rotating
        rotating_hit_list = check_for_collision_with_lists(moving_sprite, walls)

        if len(rotating_hit_list) > 0:

            max_distance = (moving_sprite.width + moving_sprite.height) / 2

            # Resolve any collisions by this weird kludge
            _circular_check(moving_sprite, walls)
            if get_distance(original_x, original_y, moving_sprite.center_x, moving_sprite.center_y) > max_distance:
                # Ok, glitched trying to rotate. Reset.
                moving_sprite.center_x = original_x
                moving_sprite.center_y = original_y
                moving_sprite.angle = original_angle

    # --- Move in the y direction
    moving_sprite.center_y += moving_sprite.change_y

    # Check for wall hit
    hit_list_x = check_for_collision_with_lists(moving_sprite, walls)
    # print(f"Post-y move {hit_list_x}")
    complete_hit_list = hit_list_x

    # If we hit a wall, move so the edges are at the same point
    if len(hit_list_x) > 0:
        if moving_sprite.change_y > 0:
            while len(check_for_collision_with_lists(moving_sprite, walls)) > 0:
                moving_sprite.center_y -= 1
            # print(f"Spot X ({self.player_sprite.center_x}, {self.player_sprite.center_y})"
            #       f" {self.player_sprite.change_y}")
        elif moving_sprite.change_y < 0:
            # Reset number of jumps
            for item in hit_list_x:
                while check_for_collision(moving_sprite, item):
                    # self.player_sprite.bottom = item.top <- Doesn't work for ramps
                    moving_sprite.center_y += 0.25

                if item.change_x != 0:
                    moving_sprite.center_x += item.change_x

            # print(f"Spot Y ({self.player_sprite.center_x}, {self.player_sprite.center_y})")
        else:
            pass
            # TODO: The code below can't execute, as "item" doesn't
            # exist. In theory, this condition should never be arrived at.
            # Collision while player wasn't moving, most likely
            # moving platform.
            # if self.player_sprite.center_y >= item.center_y:
            #     self.player_sprite.bottom = item.top
            # else:
            #     self.player_sprite.top = item.bottom
        if isinstance(moving_sprite.velocity, Vec2):
            moving_sprite.velocity = (moving_sprite.velocity[0], min(0.0, hit_list_x[0].change_y))
        else:
            moving_sprite.change_y = min(0.0, hit_list_x[0].change_y)

    # print(f"Spot D ({self.player_sprite.center_x}, {self.player_sprite.center_y})")
    moving_sprite.center_y = round(moving_sprite.center_y, 2)
    # print(f"Spot Q ({self.player_sprite.center_x}, {self.player_sprite.center_y})")

    # end_time = time.time()
    # print(f"Move 1 - {end_time - start_time:7.4f}")
    # start_time = time.time()

    loop_count = 0
    # --- Move in the x direction
    if moving_sprite.change_x:
        # Keep track of our current y, used in ramping up
        almost_original_y = moving_sprite.center_y

        # Strip off sign so we only have to write one version of this for
        # both directions
        direction = math.copysign(1, moving_sprite.change_x)
        cur_x_change = abs(moving_sprite.change_x)
        upper_bound = cur_x_change
        lower_bound: float = 0
        cur_y_change: float = 0

        exit_loop = False
        while not exit_loop:

            loop_count += 1
            # print(f"{cur_x_change=}, {upper_bound=}, {lower_bound=}, {loop_count=}")

            # Move sprite and check for collisions
            moving_sprite.center_x = original_x + cur_x_change * direction
            collision_check = check_for_collision_with_lists(moving_sprite, walls)

            # Update collision list
            for sprite in collision_check:
                if sprite not in complete_hit_list:
                    complete_hit_list.append(sprite)

            # Did we collide?
            if len(collision_check) > 0:
                # We did collide. Can we ramp up and not collide?
                if ramp_up:
                    cur_y_change = cur_x_change
                    moving_sprite.center_y = original_y + cur_y_change

                    collision_check = check_for_collision_with_lists(moving_sprite, walls)
                    if len(collision_check) > 0:
                        cur_y_change -= cur_x_change
                    else:
                        while len(collision_check) == 0 and cur_y_change > 0:
                            # print("Ramp up check")
                            cur_y_change -= 1
                            moving_sprite.center_y = almost_original_y + cur_y_change
                            collision_check = check_for_collision_with_lists(moving_sprite, walls)
                        cur_y_change += 1
                        collision_check = []

                if len(collision_check) > 0:
                    # print(f"Yes @ {cur_x_change}")
                    upper_bound = cur_x_change - 1
                    if upper_bound - lower_bound <= 0:
                        cur_x_change = lower_bound
                        exit_loop = True
                        # print(f"Exit 2 @ {cur_x_change}")
                    else:
                        cur_x_change = (upper_bound + lower_bound) // 2
                else:
                    exit_loop = True
                    # print(f"Exit 1 @ {cur_x_change}")

            else:
                # No collision. Keep this new position and exit
                lower_bound = cur_x_change
                if upper_bound - lower_bound <= 0:
                    # print(f"Exit 3 @ {cur_x_change}")
                    exit_loop = True
                else:
                    # print(f"No @ {cur_x_change}")
                    cur_x_change = (upper_bound + lower_bound) // 2 + (upper_bound + lower_bound) % 2

        # print(cur_x_change * direction, cur_y_change)
        moving_sprite.center_x = original_x + cur_x_change * direction
        moving_sprite.center_y = almost_original_y + cur_y_change
        # print(f"({moving_sprite.center_x}, {moving_sprite.center_y}) {cur_x_change * direction}, {cur_y_change}")

    # Add in rotating hit list
    for sprite in rotating_hit_list:
        if sprite not in complete_hit_list:
            complete_hit_list.append(sprite)

    # end_time = time.time()
    # print(f"Move 2 - {end_time - start_time:7.4f} {loop_count}")

    return complete_hit_list

class HKUEngine(arcade.PhysicsEngineSimple):
    def __init__(self, colliding_sprites, walls: Union[SpriteList, Iterable[SpriteList]]):

        if walls:
            if isinstance(walls, SpriteList):
                self.walls = [walls]
            else:
                self.walls = list(walls)
        else:
            self.walls = []

        self.colliding_sprite_lists = colliding_sprites

    def update(self):
        for sprite_list in self.colliding_sprite_lists:
            for sprite in sprite_list:
                _move_sprite(sprite, self.walls, ramp_up=False)
