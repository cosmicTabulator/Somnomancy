from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING
import random

from components.base_component import BaseComponent

import exceptions

if TYPE_CHECKING:
    from entity import Actor, Card

class CardZone(BaseComponent):
    parent: Actor

    def __init__(self, cards: Optional[List[Card]] = None):
        self.cards: List[Card] = []
        if cards:
            self.add_cards(cards)

    def add_card(self, card: Card) -> None:
        self.cards.append(card)
        if card.parent:
            card.parent.remove_card(card)
        card.parent = self

    def add_cards(self, cards: List[Card]) -> None:
        for card in cards:
            self.add_card(card)

    def remove_card(self, card: Card) -> None:
        try:
            self.cards.remove(card)
            card.parent = None
        except ValueError:
            raise Impossible(f"{card.name} is not in this zone.")

    @property
    def size(self) -> int:
        return len(self.cards)

class Deck(CardZone):
    discard: Optional[CardZone] = None
    def __init__(self, cards: Optional[List[Card]] = None):
        self.deck_size = 0
        super().__init__(cards)

    def link_discard(self, discard: CardZone) -> None:
        self.discard = discard

    def add_card(self, card: Card) -> None:
        super().add_card(card)
        if card.deck != self:
            card.deck = self
            self.deck_size += 1

    def remove_card(self, card: Card) -> None:
        try:
            super().remove_card(card)
            self.deck_size -= 1
        except:
            pass

    def draw_and_replace(self, number_of_cards: int = 1) -> List[Card]:
        cards_drawn: List[Card] = []
        for i in range(number_of_cards):
            shuffle()
            cards_drawn.append(self.cards[0])

        shuffle()
        return cards_drawn

    def draw_to_zone(self,  zone: CardZone, number_of_cards: int = 1) -> List[Card]:
        cards_drawn: List[Card] = []
        if number_of_cards > self.size:
            first_draw = self.size
            self.draw_to_zone(zone, first_draw)
            if self.discard:
                self.add_cards(self.discard.cards)
                self.shuffle()
                second_draw = min(number_of_cards - first_draw, self.size)
                self.draw_to_zone(zone, second_draw)
        else:
            for i in range(number_of_cards):
                cards_drawn.append(self.cards.pop())
        zone.add_cards(cards_drawn)
        return cards_drawn

    def shuffle(self) -> None:
        random.shuffle(self.cards)
