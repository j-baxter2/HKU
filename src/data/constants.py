import json

WINDOW_TITLE = "( Hungry Kitty Uprising | A BestKitty Game )"

with open("resources/maps/map2.json", "r") as file:
            map_dict = json.load(file)

M = 128

TILE_SIZE = map_dict['tilewidth']
MAP_WIDTH = map_dict['width'] * M
MAP_HEIGHT = map_dict['height'] * M
layers = map_dict['layers']
for layer in layers:
    if layer['name']=="map bounds":
        MAP_HEIGHT = layer['objects'][0]['height'] * M/TILE_SIZE
        MAP_WIDTH = layer['objects'][0]['width'] * M/TILE_SIZE


DELTA_TIME = 1/60

BAR_SPACING = 50
LINE_HEIGHT = 20
CIRCLE_RADIUS = 20

SOUND_EFFECT_VOL = 0.5
MUSIC_VOL = 0.1

UI_FONT_PATH = "resources/fonts/GWIBBLE_.ttf"
UI_FONT = "Gwibble"
UI_FONT_SIZE = 36
