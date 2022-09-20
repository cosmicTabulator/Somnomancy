from __future__ import annotations
from typing import Iterator, Tuple, List, TYPE_CHECKING

import random
import math
import tcod
import numpy as np
from enum import auto, Enum

from game_map import GameMap
import tile_types
import entities_factory

if TYPE_CHECKING:
    from engine import Engine


N = (0, -1)
S = (0, 1)
E = (1, 0)
W = (-1, 0)

directions = [N, S, E, W]

class Tiles(Enum):
    Wall = auto()
    Floor = auto()

class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> Tuple[int,int]:
        center_x = int((self.x1 + self.x2) /2)
        center_y = int((self.y1 + self.y2) /2)

        return center_x, center_y

    @property
    def inner(self) -> Tuple[slice,slice]:
        return slice(self.x1, self.x2), slice(self.y1, self.y2)

    def intersects(self, other: RectangularRoom) -> bool:
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )

def generate_dungeon(
    max_rooms:int,
    room_min_size:int,
    room_max_size:int,
    map_width:int,
    map_height:int,
    engine:Engine,
    max_monsters_per_room: int,
    max_items_per_room: int
) ->GameMap:

    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])
    map = np.full((map_width, map_height), fill_value=Tiles.Wall, order="F")

    regions = np.full((map_width, map_height), fill_value=0, order="F")

    region = 0

    rooms: List[RectangularRoom] = []

    corridors: List[List[Tuple[int, int]]] = []

    for r in range(max_rooms):

        #Math to ensure rooms line up with maze grid

        room_width = 2*random.randint(math.floor(room_min_size/2), math.floor(room_max_size/2))+1
        room_height = 2*random.randint(math.floor(room_min_size/2), math.floor(room_max_size/2))+1

        x = 2*random.randint(0, math.floor((dungeon.width - room_width - 1)/2))
        y = 2*random.randint(0, math.floor((dungeon.height - room_height - 1)/2))

        new_room = RectangularRoom(x, y, room_width, room_height)

        if any(new_room.intersects(other_room) for other_room in rooms):
            continue

        region += 1
        map[new_room.inner] = Tiles.Floor
        regions[new_room.inner] = region

        if len(rooms) == 0:
            player.place(*new_room.center, dungeon)

        place_entities(new_room, dungeon, max_monsters_per_room, max_items_per_room)

        rooms.append(new_room)

    for i in range(0, map_width, 2):
        for j in range(0, map_height, 2):
            if adjacencies(i, j, map) == 0:
                region += 1
                corridors.append(maze_fill(i, j, map))
                for tile in corridors[-1]:
                    regions[tile] = region
                    map[tile] = Tiles.Floor

    connections = {}
    for i in range(0, map_width):
        for j in range(0, map_height):
            if map[i, j] != Tiles.Floor:
                adjacent_regions = []
                for direction in get_adjacent_grid(i, j, map_width, map_height):
                    if regions[i+direction[0], j+direction[1]] not in adjacent_regions and regions[i+direction[0], j+direction[1]] > 0:
                        adjacent_regions.append(regions[i+direction[0], j+direction[1]])
                if len(adjacent_regions) > 1:
                    connections[(i, j)] = adjacent_regions

    merged = []


    while len(merged) != region:
        connection_keys = list(connections.keys())
        door = random.choice(connection_keys)
        map[door] = Tiles.Floor
        merged_regions = connections[door]
        for r in merged_regions:
            if r not in merged:
                merged.append(r)
        for pair in list(connections.items()):
            if pair[1][0] in merged and pair[1][1] in merged:
                connections.pop(pair[0])
                if random.randint(0, 50) == 0:
                    map[pair[0]] = Tiles.Floor

    for corridor in corridors:
        while shrink_dead_ends(corridor, map):
            pass

    for i in range(map_width):
        for j in range(map_height):
            if map[i, j] == Tiles.Floor:
                dungeon.tiles[i, j] = tile_types.floor

    return dungeon

def place_entities(room: RectangularRoom, dungeon: GameMap, max_monsters: int, max_items: int) -> None:
    number_of_monsters = random.randint(0, max_monsters)
    number_of_items = random.randint(0, max_items)
    for i in range(number_of_monsters):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            if random.random() < 0.8:
                entities_factory.orc.spawn(dungeon, x, y)
            else:
                entities_factory.troll.spawn(dungeon, x, y)

    for i in range(number_of_items):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            item_chance = random.random()

            if item_chance < 0.7:
                entities_factory.health_potion.spawn(dungeon, x, y)
            elif item_chance< 0.8:
                entities_factory.fireball_scroll.spawn(dungeon, x, y)
            elif item_chance < 0.9:
                entities_factory.confusion_scroll.spawn(dungeon, x, y)
            else:
                entities_factory.lightning_scroll.spawn(dungeon, x, y)

def adjacencies(x: int, y: int, map: np.ndarray) -> int:
    adjacencies = 0
    directions = get_adjacent_grid(x, y, map.shape[0], map.shape[1])
    for dir in directions:
        if map[x+dir[0], y+dir[1]] == Tiles.Floor:
            adjacencies += 1
    return adjacencies

def get_adjacent_grid(x: int, y: int, width: int, height: int, range: int = 1) -> List[Tuple[int, int]]:
    adjacent = []
    if x <= width - 1 - range:
        adjacent.append(E)
    if x >= 0+range:
        adjacent.append(W)
    if y <= height - 1 - range:
        adjacent.append(S)
    if y >= 0+range:
        adjacent.append(N)
    return adjacent

def maze_fill(x: int, y:int, map: np.ndarray) -> List[Tuple[int, int]]:
    maze = [(x, y)]
    tracker = [(x, y)]
    while len(tracker) > 0:
        i, j = tracker[-1]
        adjacent = get_adjacent_grid(i, j, map.shape[0], map.shape[1], range=2)
        filled_adjacencies = []
        for tile in adjacent:
            if map[i+(2*tile[0]), j+(2*tile[1])] == Tiles.Floor:
                filled_adjacencies.append(tile)
        for tile in filled_adjacencies:
            adjacent.remove(tile)
        if len(adjacent) == 0:
            tracker.pop(-1)
            continue
        random.shuffle(adjacent)
        direction = adjacent[0]
        maze.append((i+direction[0], j+direction[1]))
        map[maze[-1]] = Tiles.Floor
        maze.append((i+2*direction[0], j+2*direction[1]))
        map[maze[-1]] = Tiles.Floor
        tracker.append((i+2*direction[0], j+2*direction[1]))

    return maze

def shrink_dead_ends(corridor: List[Tuple[int]], map: np.ndarray) -> bool:
    for tile in corridor:
        if adjacencies(*tile, map) < 2:
            corridor.remove(tile)
            map[tile] = Tiles.Wall
            return True
    return False
