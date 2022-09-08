from __future__ import annotations

import lzma
import pickle
import math
from typing import TYPE_CHECKING

from tcod.console import Console
from tcod.map import compute_fov

import exceptions
from message_log import MessageLog
from animations import Animation
from render_functions import (
    render_bar,
    render_names_at_mouse_location,
    render_hand,
    render_viewport,
    render_deck_stats,
    render_status
    )

if TYPE_CHECKING:
    from game_map import GameMap
    from entity import Actor
    from card_suits import Suit

class Engine:

    border_width = 2
    console_width, console_height = 80, 50
    hand_width, hand_height = 20, 40
    hand_x, hand_y = border_width, border_width
    deck_stats_width, deck_stats_height = 20, 4
    deck_stats_x, deck_stats_y = border_width, border_width+hand_height+hand_y
    viewport_width, viewport_height = 40, 40
    viewport_x, viewport_y = border_width+hand_width+hand_x, border_width
    status_width, status_height = 12, 40
    status_x, status_y = border_width+viewport_width+viewport_x, border_width
    message_log_width, message_log_height = viewport_width, 4
    game_map: GameMap
    animations: List[Animation]
    card_highlighted = 0
    momentum: Tuple[int, List[Suit]]
    momentum_max = 1

    def __init__(self, player: Actor):
        self.message_log = MessageLog()
        self.mouse_location = (0, 0)
        self.player = player
        self.animations = []
        self.momentum = (self.momentum_max, [])

    def mouse_in_rect(self, x: int, y: int, width: int, height: int) -> bool:
        mouse_x, mouse_y = self.mouse_location
        return (x<=mouse_x<=(x+width-1)) and (y<=mouse_y<=(y+height-1))

    def screen_to_gamemap(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        shift_x, shift_y = self.game_map.get_map_shift(self.viewport_width-2, self.viewport_height-2)
        return(screen_x - (self.viewport_x+1)+shift_x, screen_y - (self.viewport_y+1)+shift_y)

    def gamemap_to_screen(self, game_x:int, game_y: int) -> Tuple[int, int]:
        shift_x, shift_y = self.game_map.get_map_shift(self.viewport_width-2, self.viewport_height-2)
        return(game_x-shift_x+self.viewport_x-1, game_y-shift_y+self.viewport_y-1)

    def save_as(self, filename:str) -> None:
        """Save this Engine instance as a compressed file"""
        save_data = lzma.compress(pickle.dumps(self))
        with open("savefiles/"+filename, "wb") as f:
            f.write(save_data)

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                try:
                    entity.ai.perform()
                except exceptions.Impossible:
                    pass

    def update_fov(self) -> None:
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8
        )

        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console) -> None:

        self.game_map.render(
            console,
            x=self.hand_width+(2*self.border_width)+1,
            y=self.border_width+1,
            width=self.viewport_width-2,
            height=self.viewport_width-2)

        self.message_log.render(console=console,
            x=2*self.border_width+self.deck_stats_width,
            y=2*self.border_width+self.viewport_height,
            width=self.message_log_width,
            height=self.message_log_height)

        render_viewport(
            console=console,
            x=self.viewport_x,
            y=self.viewport_y,
            width=self.viewport_width,
            height=self.viewport_height)

        render_hand(
            console=console,
            x=self.hand_x,
            y=self.hand_y,
            width=self.hand_width,
            height=self.hand_height,
            engine=self,
            hand=self.player.hand.cards,
            momentum=self.momentum)

        render_deck_stats(
            console=console,
            engine=self,
            x=self.deck_stats_x,
            y=self.deck_stats_y,
            width=self.deck_stats_width,
            height=self.deck_stats_height)

        render_status(
            console=console,
            engine=self,
            x=self.status_x,
            y=self.status_y,
            width=self.status_width,
            height = self.status_height
        )

        for animation in self.animations:
            if not animation.render(console=console, engine=self):
                self.animations.remove(animation)
