from __future__ import annotations

from typing import TYPE_CHECKING

import time
import math
import card_suits

if TYPE_CHECKING:
    from engine import Engine
    from tcod.console import Console

class Animation:
    def __init__(self):
        self.start_time = time.perf_counter()
        self.time = self.start_time
        self.delta_time = 0

    def update(self) -> None:
        self.time = time.perf_counter()
        self.delta_time = self.time - self.start_time

    def render(self, console: Console, engine: Engine) -> bool:
        '''
        Return value of true means animation is finished
        '''
        raise NotImplementedError()

class SuitScrollAnim(Animation):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.x = x
        self.y = y

    def render(self, console: Console, engine: Engine) -> bool:
        self.update()
        suit_index = int((5*self.time) % 9)+1
        suit = card_suits.Suit(suit_index)
        suit_icon, suit_color = card_suits.suit_info[suit]
        console.print(x=self.x, y=self.y, string=suit_icon, fg=suit_color)
        return True
