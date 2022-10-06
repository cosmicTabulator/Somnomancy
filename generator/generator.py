import xml.etree.ElementTree as ET

import random

from xp_loader import load_xp_string
from game_map import GameMap
from generator.prefab import Prefab

import tile_types

'''
Add support for value ranges in xml eg. rooms=10-20 -> min_rooms=10, max_rooms=20
Add support for multiple starts, ensure connectivity
'''

class Generator:
    def __init__(self, filepath, engine):
        self.engine = engine
        self.prefabs = []
        self.weights = []
        self.open_connectors = []
        self.map = None
        self.min_rooms = 0
        self.max_rooms = 0
        self.load_config(filepath)

    def generate(self):
        start = random.choice(self.start_rooms)
        x = random.randint(self.min_start_x, self.max_start_x)
        y = random.randint(self.min_start_y, self.max_start_y)
        start.place(x, y, self.map)
        self.open_connectors += start.translate_connectors(x, y)
        self.placed_rooms = 1
        for i in range(max_rooms-1):
            room = random.choice(self.prefabs)
            start_connector = random.choice(self.open_connectors)
            start_x, start_y = start_connector[0]
            end_connector = room.get_connector_facing(start_connector[1].flip())
            end_x, end_y = end_connector[0]
            dx, dy = start_connector[1].to_delta()
            for length in range(0, self.max_connector_length+1, -1):
                if room.check_match(start_x + dx*length - end_x, start_y + dy*length - end_y, self.map):
                    room.place(start_x + dx*length - end_x, start_y + dy*length - end_y, map=self.map)
                    self.map.tiles[start_x+1:start_x + dx*length, start_y+1:start_y + dy*length] = tile_types.floor
                    self.open_connectors.remove(start_connector)
                    room.connectors.remove(end_connector)
                    self.open_connectors += room.translate_connectors(start_x + dx*length - end_x, start_y + dy*length - end_y)
                    self.placed_rooms += 1
                    break
        if placed_rooms >= self.min_rooms:
            return True
        else:
            return False


    def load_config(self, filepath):
        tree = ET.parse(filepath)
        root = tree.getroot()

        if root.tag != "config":
            raise Error("Incorrect File Type")

        level = root.find("level")
        self.map = GameMap(engine=self.engine, width=int(level.get("width")), height=int(level.get("height")))
        self.min_rooms = int(level.get("min_rooms"))
        self.max_rooms = int(level.get("max_rooms"))

        rectangular_params = root.find("rectangular")
        self.min_room_width, self.max_room_width = rectangular_params.get("width").partition("-")[::2]
        self.min_room_width, self.max_room_width = int(self.min_room_width), int(self.max_room_width)
        self.min_room_height, self.max_room_height = rectangular_params.get("height").partition("-")[::2]
        self.min_room_height, self.max_room_height = int(self.min_room_height), int(self.max_room_height)
        self.min_room_doors, self.max_room_doors = rectangular_params.get("doors").partition("-")[::2]
        self.min_room_doors, self.max_room_doors = int(self.min_room_doors), int(self.max_room_doors)
        self.number_rectangular_rooms = int(rectangular_params.get("count"))

        rectangular_rooms = []
        for i in range(self.number_rectangular_rooms):
            width = random.randint(self.min_room_width, self.max_room_width)
            height = random.randint(self.min_room_height, self.max_room_height)
            tiles = np.full((width+2, height+2), fill_value=None, order="F")
            edge = []
            for x in range(width):
                for y in range(height):
                    if x>0 and x<width+1 and y>0 and y<height+1:
                        tiles[x, y] = tile_types.floor
                    else:
                        tiles[x, y] = tile_types.wall
                        if not ((x==0 or x==width+1) and (y==0 or y==height+1)):
                            edge.append((x, y))
            doors = random.randint(self.min_room_doors, self.max_room_doors)
            door_loc = []
            for i in range(doors):
                door_loc.append(random.choice(edge))
                tiles[door_loc[-1]] = tile_types.door
                edge.remove(door_loc[-1])
                adjacent = []
                for loc in edge:
                    if abs(loc[0] - door_loc[-1][0]) + abs(loc[1] - door_loc[-1][1]) <=1:
                        adjacent.append(loc)
                for loc in adjacent:
                    edge.remove(loc)
            room = Prefab(definition=None, tilemap=tiles)
            room.update_connectors(connector_loc=door_loc)
            rectangular_rooms.append(room)


        features = root.find("features")
        for element in features:
            if element.tag == "prefab":
                definition_path = element.get("definition")
                tiledata_path = element.get("filepath")
                with open(tiledata_path, "rb") as f:
                    tiledata = load_xp_string(f.read())
                definition = ET.parse(definition_path)
                prefab = Prefab(tiledata=tiledata, definition=definition)
                self.prefabs.append(prefab)
                self.weights.append(element.get("weight", default=1))
