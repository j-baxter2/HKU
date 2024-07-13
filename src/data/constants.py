import json

WINDOW_TITLE = "( Hungry Kitty Uprising | A BestKitty Game )"

with open("resources/maps/map.json", "r") as file:
            map_dict = json.load(file)

MAP_WIDTH = map_dict['width'] * map_dict['tilewidth']
MAP_HEIGHT = map_dict['height'] * map_dict['tileheight']

DELTA_TIME = 1/60
