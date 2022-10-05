import numpy as np

import tile_types
from generator_tools import Directions

class Prefab:
    def __init__(self, tiledata, definition):
        self.connectors = []
        self.tiles = self.parse_tiledata(tiledata)
        self.width, self.height = self.tiles.shape
        self.definition = definition

    def parse_tiledata(self, tiledata):
        tiles = np.full((tiledata["width"], tiledata["height"]), fill_value=None, order="F")
        tiledata_base_layer = tiledata["layer_data"][0]
        connector_loc = []
        for x in range(tiledata_base_layer["width"]):
            for y in range(tiledata_base_layer["height"]):
                cell = tiledata_base_layer["cells"][x][y]
                if cell["keycode"] != ord(" "):
                    raise Error("Unrecognized Symbol at " + str(x) + ", " + str(y))
                bg = (cell["back_r"], cell["back_g"], cell["back_b"])
                if bg = (255, 255, 255):
                    tiles[x, y] = tile_types.floor
                elif bg = (255, 0, 0):
                    tiles[x, y] = tile_types.door
                    connector_loc.append((x, y))
                elif bg=(255, 255, 0):
                    tiles[x, y] = tile_types.floor
                    connector_loc.append((x, y))
                elif bg = (156, 156, 156):
                    tiles[x, y] = tile_types.wall

        for connector in connector_loc:
            x, y = connector
            if tiles[x+1, y] == tile_types.floor:
                self.connectors.append(connector, Directions.W)
            elif tiles[x-1, y] == tile_types.floor:
                self.connectors.append(connector, Directions.E)
            elif tiles[x, y+1] == tile_types.floor:
                self.connectors.append(connector, Directions.N)
            elif tiles[x, y-1] == tile_types.floor:
                self.connectors.append(connector, Directions.S)

        return tiles

    def check_match(self, x: int, y: int, map: np.ndarray) -> bool:
        map_slice = map[x:self.width+x, y:self.height+y]
        for i in range(width):
            for j in range(height):
                if self.tiles[i, j] != None and self.tiles[i, j] != map_slice[i, j]:
                    return False
        return True
