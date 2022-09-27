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

class Directions(Enum):

    N = 0
    E = 1
    S = 2
    W = 3

    def rot(self, times=1):
        return Directions((self.value + times) % 4)

    def flip(self):
        return self.rot(times=2)

    def to_delta(self):
        if self.value == 0:
            return (0, -1)
        elif self.value == 1:
            return (1, 0)
        elif self.value == 2:
            return (0, 1)
        else:
            return (-1, 0)

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

    @property
    def outer(self) -> Tuple[slice,slice]:
        return slice(self.x1-1, self.x2+1), slice(self.y1-1, self.y2+1)

    def intersects(self, other: RectangularRoom) -> bool:
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )

    def in_bounds(self, map_width: int, map_height: int) -> bool:
        return (
            self.x1 > 1
            and self.x2 < map_width-1
            and self.y1 > 1
            and self.y2 < map_height-1
        )

def get_adjacent(x, y, width, height):
    adjacent = []
    if x+1 < width:
        adjacent.append((x+1, y))
    if x-1 >= 0:
        adjacent.append((x-1, y))
    if y+1 < height:
        adjacent.append((x, y+1))
    if y-1 >= 0:
        adjacent.append((x, y-1))
    return adjacent

MAX_VAL = 999999

def djikstra_fill(map, source):
    d_map = np.full(map.shape, fill_value=MAX_VAL, order="F")
    width, height = map.shape
    d_map[source] = 0
    changes = True
    while True:
        changes = False
        for i in range(width):
            for j in range(height):
                if map[i, j]:
                    adjacent = get_adjacent(i, j, width, height)
                    val = d_map[i, j]
                    for tile in adjacent:
                        val = min(val, d_map[tile]+1)
                    if val < d_map[i, j]:
                        d_map[i, j] = val
                        changes = True
        if not changes:
            break

    return d_map

def path(map, start, finish):
    start_x, start_y = start
    finish_x, finish_y = finish

    x, y = start

    path = [(x, y)]
    d_map = djikstra_fill(map, finish)

    while path[-1] != finish:
        x, y = path[-1]
        adjacent = get_adjacent(x, y, *map.shape)
        val = d_map[x, y]
        for tile in adjacent:
            val = min(val, d_map[tile])
        lowest_tiles = [tile for tile in adjacent if d_map[tile] == val]
        path.append(random.choice(lowest_tiles))

    return path

def in_bounds(x : int, y : int, width : int, height : int) -> bool:
    return (x >= 0 and x < width and y >= 0 and y < height)

def clear_path(x : int, y : int, dir : Directions, step_size : int, map : GameMap) -> bool:
    dx, dy = dir.to_delta()
    for i in range(1, step_size+1):
        if map.tiles[x+i*dx, y+i*dy] != tile_types.wall:
            return False
    return True

class Tunneler:
    def __init__(self, start, lifespan, start_dir, step_size, turn_prob):
        self.x, self.y = start
        self.lifespan = lifespan
        self.dir = start_dir
        self.step_size = step_size
        self.turn_prob = turn_prob
        self.room_prob = 0.6
        self.branch_prob = 0.3
        self.children = []

    def update(self, map):
        width, height = map.width, map.height
        if random.random() < self.turn_prob:
            s = random.randint(0, 1)
            self.dir = self.dir.rot(2*s - 1)
        dx, dy = self.dir.to_delta()
        end_x, end_y = self.x+self.step_size*dx, self.y+self.step_size*dy
        if (
            in_bounds(x=end_x, y=end_y, width=map.width, height=map.height)
            and clear_path(self.x, self.y, self.dir, self.step_size, map)
        ):
            for i in range(1, self.step_size+1):
                if random.random() < self.room_prob:
                    s = random.randint(0, 1)
                    self.children.append(Builder(
                        x=self.x+i*dx,
                        y=self.y+i*dy,
                        dir=self.dir.rot(2*s - 1),
                        room_min_size=6,
                        room_max_size=10
                    ))
                if random.random() < self.branch_prob:
                    s = random.randint(0, 1)
                    self.children.append(Tunneler(
                        start=(self.x+i*dx, self.y+i*dy),
                        lifespan=5,
                        start_dir=self.dir.rot(2*s-1),
                        step_size=self.step_size,
                        turn_prob=self.turn_prob
                        ))
                map.tiles[self.x+i*dx, self.y+i*dy] = tile_types.floor
            self.x, self.y = end_x, end_y
            self.lifespan -= 1
            if self.lifespan == 0:
                for dir in [dir for dir in Directions if dir != self.dir]:
                    if random.random() < self.branch_prob:
                        self.children.append(Tunneler(
                            start=(self.x+i*dx, self.y+i*dy),
                            lifespan=5,
                            start_dir=dir,
                            step_size=self.step_size,
                            turn_prob=self.turn_prob
                            ))
        else:
            self.lifespan = 0

class Builder:
    def __init__(self, x: int, y : int, dir : Directions, room_min_size: int, room_max_size : int) -> None:
        self.x, self.y = x, y
        self.dir = dir
        self.lifespan = 1
        self.children = []
        self.room_min_size = room_min_size
        self.room_max_size = room_max_size

    def update(self, map) -> None:
        candidates = []
        room_width = random.randint(self.room_min_size, self.room_max_size)
        room_height = random.randint(self.room_min_size, self.room_max_size)
        dx, dy = self.dir.to_delta()
        shift = random.randint(0, room_width*abs(dy) + room_height*abs(dx))
        room = RectangularRoom(
            x=self.x+(room_width+1)*dx-shift*abs(dy),
            y=self.y+(room_height+1)*dy-shift*abs(dx),
            width=room_width,
            height=room_height)
        if room.in_bounds(map_width=map.width, map_height=map.height):
            if np.all(map.tiles[room.outer] == tile_types.wall):
                map.tiles[room.inner] = tile_types.floor
                map.tiles[self.x+dx, self.y+dy] = tile_types.door
                place_entities(room, map, 2, 2)
                #rooms.append(room)
        self.lifespan = 0

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

    rooms: List[RectangularRoom] = []

    dungeon.tiles[map_width//2, map_height//2] = tile_types.floor
    player.place(map_width//2, map_height//2, dungeon)

    tunnelers = [Tunneler(
        start=(map_width//2, map_height//2),
        lifespan=5,
        start_dir=Directions.N,
        step_size=7,
        turn_prob=0.5
    )]

    dead = []
    children = []

    number_generations = 10

    for i in range(number_generations):
        while tunnelers:
            for t in tunnelers:
                t.update(dungeon)
                if t.lifespan == 0:
                    dead.append(t)
            for t in dead:
                tunnelers.remove(t)
                children += t.children
            dead = []
        for child in children:
            tunnelers.append(child)
        children = []

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
