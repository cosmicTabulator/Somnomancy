from entity import Card
from components import card_effects

from card_suits import Suit

sprint_card = Card(
    char="-",
    color=(255, 255, 0),
    name="Sprint",
    text="Move up to 3 spaces",
    effect=card_effects.MoveEffect(move_distance=3),
    suits=[Suit.WINGS]
)

strike_card = Card(
    char="-",
    color=(255, 255, 0),
    name="Strike",
    text="Attack an adjacent enemy for 5 damage",
    effect=card_effects.AttackEffect(attack_range=1, attack_damage=5),
    suits=[Suit.BLADES]
)
