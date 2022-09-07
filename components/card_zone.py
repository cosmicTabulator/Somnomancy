from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING
import random

from components.base_component import BaseComponent

import exceptions

if TYPE_CHECKING:
    from entity import Actor, Card

class CardZone(BaseComponent):
    parent: Actor

    def __init__(self, cards: Optional[List[Card]]):
        self.cards: List[Card] = []
        if cards:
            self.cards = cards

    def add_card(self, card: Card) -> None:
        self.cards.append(card)
        card.zone.remove_card(card)
        card.zone = self

    def add_cards(self, cards: List[Card]) -> None:
        for card in cards:
            add_card(card)

    def remove_card(self, card: Card) -> None:
        try:
            self.cards.remove(card)
            card.zone = None
        except ValueError:
            raise Impossible(f"{card.name} is not in this zone.")

    @property
    def size(self) -> int:
        return len(self.cards)

class Deck(CardZone):

    def __init__(self, cards: Optional[List[Card]]):
        super().__init__(cards)
        self.deck_size = len(self.cards)

    def add_card(self, card: Card) -> None:
        super().add_card(card)
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
        number_of_cards = min(len(self.cards), number_of_cards)
        for i in range(number_of_cards):
            cards_drawn.append(self.cards.pop())
        zone.add_cards(cards_drawn)
        return cards_drawn

    def shuffle(self) -> None:
        random.shuffle(self.cards)
