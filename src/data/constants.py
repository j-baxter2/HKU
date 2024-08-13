import json

WINDOW_TITLE = "( Hungry Kitty Uprising | A BestKitty Game )"

with open("resources/maps/map2.json", "r") as file:
            map_dict = json.load(file)

TILE_SIZE = map_dict['tilewidth']
MAP_WIDTH = map_dict['width'] * 128
MAP_HEIGHT = map_dict['height'] * 128

DELTA_TIME = 1/60

BAR_SPACING = 50
LINE_HEIGHT = 20
CIRCLE_RADIUS = 20

SOUND_EFFECT_VOL = 0.1
MUSIC_VOL = 0.2

UI_FONT_PATH = "resources/fonts/GWIBBLE_.ttf"
UI_FONT = "Gwibble"
UI_FONT_SIZE = 36
