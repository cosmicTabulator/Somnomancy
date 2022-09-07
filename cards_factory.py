from entity import Card
from components import card_effects

from card_suits import Suit

sprint_card = Card(
    char="-",
    color=(255, 255, 0),
    name="Sprint",
    text="Move up to 3 spaces",
    effect=card_effects.MoveEffect(move_distance=3),
    suits=[Suit.WINGS, Suit.CANDLES, Suit.EYES]
)
