from __future__ import annotations

import copy
import math
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING, Union

from render_order import RenderOrder
from card_suits import Suit

if TYPE_CHECKING:
    from compenents.ai import BaseAI
    from compenents.fighter import Fighter
    from components.consumable import Consumable
    from components.inventory import Inventory
    from game_map import GameMap
    from components.card_zone import CardZone, Deck
    from card_effects import CardEffect

T = TypeVar("T", bound="Entity")

class Entity:

    parent: Union[GameMap, Inventory, CardZone]

    def __init__(
        self,
        parent: Optional[GameMap] = None,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255,255,255),
        name: str = "<Unnamed>",
        blocks_movement: bool = False,
        render_order: RenderOrder = RenderOrder.CORPSE,
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        if parent:
            self.parent=parent
            parent.entities.add(self)

    @property
    def gamemap(self) -> GameMap:
        return self.parent.gamemap

    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.parent = gamemap
        gamemap.entities.add(clone)
        return clone

    def place(self, x: int, y: int, gamemap: Optional[GameMap] = None) -> None:
        self.x = x
        self.y = y
        if gamemap:
            if hasattr(self, "parent"):
                if self.parent is self.gamemap:
                    self.gamemap.entities.remove(self)
            self.parent = gamemap
            gamemap.entities.add(self)

    def distance(self, x: int, y: int) -> float:
        return math.sqrt((x - self.x)**2 + (y-self.y)**2)

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy

class Actor(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        ai_cls: Type[BaseAI],
        fighter: Fighter,
        inventory: Inventory,
        card_handler: Optional[Tuple[Deck, CardZone, CardZone]] = None,
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=True,
            render_order=RenderOrder.ACTOR
        )

        self.ai: Optional[BaseAI] = ai_cls(self)

        self.fighter = fighter
        self.fighter.parent = self

        self.inventory = inventory
        self.inventory.parent = self

        if card_handler:
            for zone in card_handler:
                zone.parent = self
            self.deck, self.hand, self.discard = card_handler

    @property
    def is_alive(self) -> bool:
        return bool(self.ai)

class Item(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        consumable: Consumable
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=False,
            render_order=RenderOrder.ITEM
        )

        self.consumable = consumable
        self.consumable.parent = self

class Card(Entity):
    def __init__(
        self,
        *,
        char = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        text: str = "<None>",
        effect: CardEffect,
        suits: List[Suit],
        parent: Optional[CardZone] = None
    ):
        super().__init__(
            char=char,
            name=name,
            color=color,
            render_order=RenderOrder.ITEM
        )
        self.text = text
        self.effect = effect
        self.effect.parent = self
        self.suits=suits
        deck: Optional[Deck] = None
        self.parent = parent

    @property
    def gamemap(self) -> GameMap:
        return self.parent.gamemap

    def return_to_deck(self) -> None:
        if self.deck:
            self.deck.add_card(self)
        else:
            raise Impossible(f"{self.name} has no deck defined!")

    def add_to_deck(self, deck: Deck) -> None:
        self.deck = deck

    def move_to_zone(self, zone: CardZone) -> None:
        zone.add_card(self)
