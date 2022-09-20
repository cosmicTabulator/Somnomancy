from __future__ import annotations

from typing import Iterable, Iterator, Optional, TYPE_CHECKING

import numpy as np  # type: ignore
from tcod.console import Console

from entity import Actor, Item
import tile_types
import icons

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

class GameMap:
    def __init__(self, engine: Engine, width: int, height: int, entities: Iterable[Entity] = ()):
        self.engine = engine
        self.width = width
        self.height = height
        self.entities = set(entities)

        self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")

        self.visible = np.full((width, height), fill_value=False, order="F")
        self.explored = np.full((width, height), fill_value=False, order="F")

    @property
    def gamemap(self) -> GameMap:
        return self

    @property
    def actors(self) -> Iterator[Actor]:
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    @property
    def items(self) -> Iterator[Item]:
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Item)
        )

    @property
    def player_location(self) -> Tuple[int, int]:
        return (self.engine.player.x, self.engine.player.y)

    def get_map_shift(self, width: int, height: int) -> Tuple[int, int]:
        horizontal_radius = int(width/2)
        vertical_radius = int(height/2)
        left_bound = self.player_location[0]-horizontal_radius
        upper_bound = self.player_location[1]-vertical_radius
        left_bound = max(0, min(left_bound, self.width - width))
        upper_bound = max(0, min(upper_bound, self.height - height))
        return (left_bound, upper_bound)

    def get_centered_map_slice(self, width: int, height: int, map: np.ndarray) -> np.ndarray:
        horizontal_radius = int(width/2)
        vertical_radius = int(height/2)
        left_bound = self.player_location[0]-horizontal_radius
        upper_bound = self.player_location[1]-vertical_radius
        left_bound = max(0, min(left_bound, self.width - width))
        upper_bound = max(0, min(upper_bound, self.height - height))
        right_bound = width + left_bound
        lower_bound = height + upper_bound
        return map[left_bound: right_bound, upper_bound: lower_bound]

    def get_blocking_entity_at_location(self, location_x: int, location_y: int) -> Optional[Entity]:
        for entity in self.entities:
            if entity.blocks_movement and entity.x == location_x and entity.y == location_y:
                return entity

        return None

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor

        return None

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console, x: int, y: int, width: int, height: int) -> None:
        '''
        viewmap = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD
        )
        '''
        viewmap = self.tiles["light"]
        viewslice = self.get_centered_map_slice(width=width, height=height, map=viewmap)
        console.tiles_rgb[x:(x+width), y:(y+height)] = viewslice

        entities_sorted_for_rendering = sorted(self.entities, key=lambda x: x.render_order.value)

        shift_x, shift_y = self.get_map_shift(width=width, height=height)

        for actor in self.actors:
            attack_pattern = actor.ai.get_attack()
            if attack_pattern and self.visible[actor.x, actor.y]:
                for tile in attack_pattern.get_tile_list():
                    tile_x, tile_y = tile
                    if self.explored[tile_x, tile_y] and self.tiles[tile_x, tile_y]["transparent"]:
                        console.print(
                            x=x+tile_x-shift_x,
                            y=y+tile_y-shift_y,
                            string=icons.attack_indicator[0],
                            fg=icons.attack_indicator[1]
                        )


        for entity in entities_sorted_for_rendering:
            if self.visible[entity.x, entity.y]:
                console.print(x=x+entity.x-shift_x, y=y+entity.y-shift_y, string=entity.char, fg=entity.color)
