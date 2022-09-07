from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from input_handler import (
    ActionOrHandler,
    SingleRangedAttackHandler,
    )

import color

from actions import CardAction
from entity import Card, Actor
from components.base_component import BaseComponent
from exceptions import Impossible

class CardEffect(BaseComponent):
    parent: Card

    def get_action(self, user: Actor) -> Optional[ActionOrHandler]:
        return CardAction(user, self)

    def activate(self, action: CardAction) -> None:
        raise NotImplementedError()

    def discard(self) -> None:
        self.parent.move_to_zone(self.engine.player.discard)

class MoveEffect(CardEffect):
    def __init__(self, move_distance: int):
        self.move_distance = move_distance

    def get_action(self, user: Actor) -> SingleRangedAttackHandler:
        return SingleRangedAttackHandler(
            self.engine,
            callback=lambda xy: CardAction(self.engine.player, self.parent, xy)
        )

    def activate(self, action: CardAction) -> None:
        target_x, target_y = action.target_xy
        dx = target_x - self.engine.player.x
        dy = target_y - self.engine.player.y
        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot move somewhere you cannot see!")
        if not self.engine.game_map.in_bounds(target_x, target_y):
            raise exceptions.Impossible("That way is blocked.")
        if not self.engine.game_map.tiles["walkable"][target_x, target_y]:
            raise exceptions.Impossible("That way is blocked.")
        if self.engine.game_map.get_blocking_entity_at_location(target_x, target_y):
            raise exceptions.Impossible("That way is blocked.")
        if max(dx, dy) > self.move_distance:
            raise Impossible("You cannot move that far.")

        self.engine.player.move(dx, dy)
        self.discard()

class AttackEffect(CardEffect):
    def __init__(self, attack_range: int, attack_damage: int):
        self.attack_range = attack_range
        self.attack_damage = attack_damage

    def get_action(self, user: Actor) -> SingleRangedAttackHandler:
        return SingleRangedAttackHandler(
            self.engine,
            callback=lambda xy: CardAction(self.engine.player, self.parent, xy)
        )

    def activate(self, action: CardAction) -> None:
        target_x, target_y = action.target_xy
        target_actor = action.target_actor
        if not target_actor:
            raise Impossible("There is nothing to attack there.")
        damage = max(0, self.attack_damage - target_actor.fighter.defense)
        dx = target_x - self.engine.player.x
        dy = target_y - self.engine.player.y
        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot attack somewhere you cannot see!")
        if max(dx, dy) > self.attack_range:
            raise Impossible("You cannot attack that far away.")

        target_actor.fighter.hp -= damage
        self.engine.message_log.add_message(f"You strike the {target_actor.name} for {damage} damage!", color.player_atk)
        self.discard()
