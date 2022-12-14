from __future__ import annotations

import random
from typing import List, Optional, Tuple, TYPE_CHECKING

import numpy as np
import tcod

from components.attacks import AttackPattern, AdjacentAttack
from actions import Action, BumpAction, MeleeAction, MoveAction, WaitAction

if TYPE_CHECKING:
    from entity import Actor

class BaseAI(Action):

    entity: Actor

    def perform(self) -> None:
        raise NotImplementedError()

    def get_attack(self) -> Optional[AttackPattern]:
        raise NotImplementedError()

    def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:

        cost = np.array(self.entity.gamemap.tiles["walkable"], dtype=np.int8)

        #If there's a blocking entity and the cost isn't 0 (blocking)
        for entity in self.entity.gamemap.entities:
            if entity.blocks_movement and cost[entity.x, entity.y]:
                #Increase cost
                #Result: Higher cost encourages enemies to surround the player instead of crowd behind eachother
                cost[entity.x, entity.y] += 10

        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.entity.x, self.entity.y)) #Start position

        #Compute path to the destination and remove the start point
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        #Convert to list of tuples
        return [(index[0], index[1]) for index in path]

class ConfusedEnemy(BaseAI):
    def __init__(self, entity: Actor, previous_ai: Optional[BaseAI], turns_remaining: int):
        super().__init__(entity)
        self.previous_ai = previous_ai
        self.turns_remaining = turns_remaining

    def perform(self) -> None:
        if self.turns_remaining <= 0:
            self.engine.message_log.add_message(f"The {self.entity.name} is no longer confused.")
            self.entity.ai = self.previous_ai
        else:
            direction_x, direction_y = random.choice(
                [
                (-1, -1),
                (0, -1),
                (1, -1),
                (-1, 0),
                (1, 0),
                (-1, 1),
                (0, 1),
                (1, 1)
                ]
            )
            self.turns_remaining -= 1
            return BumpAction(self.entity, direction_x, direction_y).perform()

    def get_attack(self) -> Optional[AttackPattern]:
        return None


class HostileEnemy(BaseAI):
    def __init__(self, entity: Actor):
        super().__init__(entity)
        self.path: List[Tuple[Int, Int]] = []

    def perform(self) -> None:
        target = self.engine.player
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx), abs(dy)) #Chebyshev Distance

        if self.engine.game_map.visible[self.entity.x, self.entity.y]:
            if distance <= 1:
                return MeleeAction(self.entity, dx, dy).perform()

            self.path = self.get_path_to(target.x, target.y)

        if self.path:
            dest_x, dest_y = self.path.pop(0)
            return MoveAction(self.entity, dest_x - self.entity.x, dest_y - self.entity.y).perform()

        return WaitAction(self.entity).perform()

    def get_attack(self) -> Optional[AttackPattern]:
        return None

class BansheeAI(BaseAI):
    def __init__(self, entity: Actor, move_speed: int=3, attack_radius: int=1):
        super().__init__(entity)
        self.path: List[Tuple[int, int]] = []
        self.move_speed = move_speed
        self.attack_radius = attack_radius

    def perform(self) -> None:
        if self.engine.game_map.visible[self.entity.x, self.entity.y]:

            for tile in self.get_attack().get_tile_list():
                target = self.engine.game_map.get_actor_at_location(*tile)
                if target:
                    dx, dy = target.x - self.entity.x, target.y - self.entity.y
                    MeleeAction(self.entity, dx, dy).perform()

            target = self.engine.player

            self.path = self.get_path_to(target.x, target.y)
            self.path = self.path[:-1]

        if self.path:
            move_distance = min(self.move_speed, len(self.path))
            for i in range(move_distance):
                dest_x, dest_y = self.path.pop(0)
            return MoveAction(self.entity, dest_x - self.entity.x, dest_y - self.entity.y).perform()


    def get_attack(self) -> AttackPattern:
        return AdjacentAttack(x=self.entity.x, y=self.entity.y, radius=self.attack_radius, gamemap=self.engine.game_map)
