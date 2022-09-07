from __future__ import annotations

from typing import List, TYPE_CHECKING

import color
import card_suits
import tcod

if TYPE_CHECKING:
    from tcod import Console
    from engine import Engine
    from game_map import GameMap

def get_names_at_location(x: int, y: int, game_map: GameMap) -> str:
    if not game_map.in_bounds(x,y) or not game_map.visible[x, y]:
        return ""

    names = ", ".join(entity.name for entity in game_map.entities if entity.x == x and entity.y == y)

    return names.capitalize()

def render_bar(
    console: Console,
    x: int,
    y: int,
    current_value: int,
    maximum_value: int,
    total_width: int,
    string: str
) -> None:
    bar_width = int(float(current_value) / maximum_value * total_width)

    console.draw_rect(x=x, y=y, width=total_width, height=1, ch=1, bg=color.bar_empty)

    if bar_width > 0:
        console.draw_rect(x=x, y=y, width=bar_width, height=1, ch=1, bg=color.bar_filled)

    console.print(x=x+1, y=y, string=string+f": {current_value}/{maximum_value}", fg=color.bar_text)

def render_names_at_mouse_location(
    console: Console,
    x: int,
    y: int,
    width: int,
    height: int,
    engine: Engine,
) -> None:
    mouse_x, mouse_y = engine.screen_to_gamemap(*engine.mouse_location)

    names_at_mouse_location = get_names_at_location(x=mouse_x, y=mouse_y, game_map=engine.game_map)

    console.print_box(x=x, y=y, width=width, height=height, string=names_at_mouse_location)

def render_hand(
    console: Console,
    x: int,
    y: int,
    width: int,
    height: int,
    engine: Engine,
    hand: List[Card],
    momentum: Tuple[int, List[card_suits.Suit]]
) -> None:
    hand_size = len(hand)
    console.draw_frame(
        x=x,
        y=y,
        width=width,
        height=height,
        clear=True,
        fg=(255, 255, 255),
        bg=(0,0,0)
    )

    console.print_box(x=x, y=y, width=width, height=1, alignment=tcod.CENTER, string="┤Hand├")
    console.print(x=x+1, y=y+1, string=f"Momentum: {momentum[0]}", fg=color.momentum)
    for i, suit in enumerate(momentum[1]):
        suit_char, suit_color = card_suits.suit_info[suit]
        console.print(x=x+1+i, y=y+2, string=suit_char, fg=suit_color)

    if hand_size > 0:
        print_card = None
        for i, card in enumerate(hand):
            if engine.mouse_in_rect(x=x+1, y=y+i+3, width=width-2, height=1):
                fg=color.highlight
                console.print(x+1, y+i+3, "►", fg=color.highlight)
                print_card = i
            else:
                fg=color.white
            console.print(x+2, y+i+3, f"{card.name}", fg=fg)
            '''
            TODO: display suits in hand window
            for index, suit in enumerate(card.suits):
                suit_char, suit_color = card_suits.suit_info[suit]
                console.print(x=x+1+, y=y+1+i, string=suit_char, fg=suit_color)
            '''
        if print_card is not None:
            y_offset = 2
            if y+print_card+3 > 25:
                y_offset = -2-height
            render_card(console=console, card=hand[i], x=engine.mouse_location[0]+2, y=engine.mouse_location[1]+y_offset, width=12, height=15)
    else:
        console.print(x+1, y+1, "(Empty)")

def render_card(
    console: Console,
    card: Card,
    x: int,
    y: int,
    width: int,
    height: int
) -> None:
    console.draw_frame(x=x, y=y, width=width, height=height, clear=True, fg=(255,255,255), bg=(0,0,0))
    console.print_box(
        x=x+2,
        y=y+1,
        height=1,
        width=width-4,
        string=card.name,
        fg=(255, 255, 255),
        alignment=tcod.CENTER
    )
    console.draw_rect(
        x=x+2,
        y=y+2,
        height=1,
        width=width-4,
        ch=ord("-"),
        fg=(255, 255, 255)
    )
    console.print_box(
        x=x+2,
        y=y+4,
        height=height-5,
        width=width-4,
        string=card.text,
        fg=(255, 255, 255),
        alignment=tcod.LEFT
    )
    for index, suit in enumerate(card.suits):
        suit_char, suit_color = card_suits.suit_info[suit]
        console.print(x=x+1, y=y+1+index, string=suit_char, fg=suit_color)
        console.print(x=x+width-2, y=y+height-2-index, string=suit_char, fg=suit_color)

def render_viewport(
    console: Console,
    x: int,
    y: int,
    width: int,
    height: int
) -> None:
    console.draw_frame(x=x, y=y, width=width, height=height, clear=False, fg=(255,255,255), bg=(0,0,0))

def get_highlight(engine: Engine, x: int, y: int, width: int, height: int) -> Tuple[int, int, int]:
    if engine.mouse_in_rect(x=x, y=y, width=width, height=height):
        return color.highlight
    return color.white

def render_deck_stats(
    console: Console,
    engine: Engine,
    x: int,
    y: int,
    width: int,
    height: int
) -> None:

    console.draw_frame(x=x, y=y, width=width, height=height, clear=False, fg=(255,255,255), bg=(0,0,0))
    fg=get_highlight(engine=engine, x=x+1, y=y+1, width=width, height=1)
    console.print(x=x+1, y=y+1, string=f"Deck: {engine.player.deck.size}/{engine.player.deck.deck_size}", fg=fg)
    fg=get_highlight(engine=engine, x=x+1, y=y+2, width=width, height=1)
    console.print(x=x+1, y=y+2, string=f"Discard: {engine.player.discard.size}", fg=fg)

def render_status(
    console: Console,
    engine: Engine,
    x: int,
    y: int,
    width: int,
    height: int
) -> None:
    console.draw_frame(x=x, y=y, width=width, height=height, clear=False, fg=(255,255,255), bg=(0,0,0))
    render_bar(
        console=console,
        current_value=engine.player.fighter.hp,
        maximum_value=engine.player.fighter.max_hp,
        total_width=width-2,
        string="HP",
        x=x+1,
        y=y+1
    )
    render_names_at_mouse_location(console=console, x=x+1, y=y+2, width=width-2, height=3, engine=engine)
