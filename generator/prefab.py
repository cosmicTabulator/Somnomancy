from __future__ import annotations, TYPE_CHECKING

import random

import numpy as np

import tile_types
from generator.generator_tools import Directions

if TYPE_CHECKING:
    from game_map import GameMap

class Prefab:
    def __init__(self, definition, tiledata=None, tilemap=None):
        self.connectors = []
        self.tiles = None
        if tiledata:
            self.parse_tiledata(tiledata)
        elif tilemap:
            self.tiles = tilemap
        else:
            raise Error("No tiledata or tilemap")
        self.width, self.height = self.tiles.shape
        self.definition = definition

    def parse_tiledata(self, tiledata):
        self.tiles = np.full((tiledata["width"], tiledata["height"]), fill_value=None, order="F")
        tiledata_base_layer = tiledata["layer_data"][0]
        connector_loc = []
        for x in range(tiledata_base_layer["width"]):
            for y in range(tiledata_base_layer["height"]):
                cell = tiledata_base_layer["cells"][x][y]
                if cell["keycode"] != ord(" "):
                    raise Error("Unrecognized Symbol at " + str(x) + ", " + str(y))
                bg = (cell["back_r"], cell["back_g"], cell["back_b"])
                if bg = (255, 255, 255):
                    self.tiles[x, y] = tile_types.floor
                elif bg = (255, 0, 0):
                    self.tiles[x, y] = tile_types.door
                    connector_loc.append((x, y))
                elif bg=(255, 255, 0):
                    self.tiles[x, y] = tile_types.floor
                    connector_loc.append((x, y))
                elif bg = (156, 156, 156):
                    self.tiles[x, y] = tile_types.wall

        self.update_connectors(connector_loc=connector_loc)

    def update_connectors(self, connector_loc, clear=False) -> None:
        if clear:
            self.connectors = []
        for connector in connector_loc:
            x, y = connector
            if self.tiles[x+1, y] == tile_types.floor:
                self.connectors.append(connector, Directions.W)
            elif self.tiles[x-1, y] == tile_types.floor:
                self.connectors.append(connector, Directions.E)
            elif self.tiles[x, y+1] == tile_types.floor:
                self.connectors.append(connector, Directions.N)
            elif self.tiles[x, y-1] == tile_types.floor:
                self.connectors.append(connector, Directions.S)

    def place(self, x: int, y: int, map: GameMap) -> None:
        map.tiles[x:self.width+x, y:self.height+y] = self.tiles

    def translate_connectors(self, x: int, y: int):
        translated = [((connector[0][0]+x, connector[0][1]+y), connector[1]) for connector in self.connectors]
        return translated

    def get_connector_facing(self, dir: Directions):
        random.shuffle(self.connectors)
        for connector in self.connectors:
            if connector[1] == dir:
                return connector

        return None

    def check_match(self, x: int, y: int, map: GameMap) -> bool:
        map_width, map_height = map.shape
        if x+self.width>map_width or x<0 or y+self.height>map_height or y<0:
            return False
        map_slice = map.tiles[x:self.width+x, y:self.height+y]
        for i in range(width):
            for j in range(height):
                if self.tiles[i, j] != None and self.tiles[i, j] != map_slice[i, j]:
                    return False
        return True
