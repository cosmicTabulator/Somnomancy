import traceback

import tcod

import color
import exceptions
import input_handler
import setup_game

'''
by cosmicTabulator
September 6, 2022

v0.1
-Updated rendering to new layout
-Fixed input handler issues with new layout
-Added Card entity and CardZone components
-Changed tileset to Unknown_curses_12x12.png (DwarfFortress tile repository, author unknown)
-Reorganized asset structure
-Added card suits (Wings, Blades, Flames, Eyes, Candles, Walls, Doors, Storms, Songs)
-Implemented map scrolling
-Implemented animation framework

TODO:
-Display card suit in hand window
-Deck and Discard viewing
-Play cards with mouse or keyboard
    -Consistent card highlighting between mouse and keyboard
-Framerate montoring

Future Plans
-Minimap
-Start in dungeon, battle to surface world
-Redo level generator
-Change menu background

'''

def save_game(handler: input_handler.BaseEventHandler, filename: str) -> None:
    if isinstance(handler, input_handler.EventHandler):
        handler.engine.save_as(filename)
        print("Game saved.")

def main() -> None:
    """Script entry point."""

    WIDTH, HEIGHT = 80, 50

    tileset = tcod.tileset.load_tilesheet(
        "assets/tilemaps/Unknown_curses_12x12.png", 16, 16, tcod.tileset.CHARMAP_CP437,
    )

    handler: input_handler.BaseEventHandler = setup_game.MainMenu()

    # Create the main console.
    console = tcod.Console(WIDTH, HEIGHT, order="F")
    # Create a window based on this console and tileset.
    with tcod.context.new(  # New window for a console of size columns×rows.
        columns=console.width, rows=console.height, tileset=tileset, title="Somnomancy"
    ) as context:
        try:
            while True:  # Main loop, runs until SystemExit is raised.
                console.clear()
                handler.on_render(console=console)
                context.present(console)

                try:
                    for event in tcod.event.get():
                        context.convert_event(event)
                        handler = handler.handle_events(event)
                except Exception:
                    traceback.print_exc()
                    if isinstance(handler, input_handler.EventHandler):
                        handler.engine.message_log.add_message(traceback.format_exc(), color.error)

        except exceptions.QuitWithoutSaving:
            raise
        except SystemExit: #Save and Quit
            save_game(handler, "savegame.sav")
            raise
        except BaseException: #Save on any other unexpected exception
            save_game(handler, "savegame.sav")
            raise


if __name__ == "__main__":
    main()
