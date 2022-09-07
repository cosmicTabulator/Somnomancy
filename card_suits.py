from enum import auto, Enum

class Suit(Enum):
    WINGS = auto()
    BLADES = auto()
    FLAMES = auto()
    WALLS = auto()
    DOORS = auto()
    CANDLES = auto()
    EYES = auto()
    SONGS = auto()
    STORMS = auto()

suit_info = {
    Suit.WINGS: ("%", (0xFF, 0xFF, 0xFF)),
    Suit.BLADES: ("↑", (0x66, 0x66, 0x66)),
    Suit.FLAMES: ("^", (0xFF, 0x40, 0x00)),
    Suit.WALLS: ("≡", (0xBF, 0xBF, 0xBF)),
    Suit.DOORS: ("Ω", (0x8A, 0x55, 0x25)),
    Suit.CANDLES: ("¡", (0xFF, 0xFF, 0x00)),
    Suit.EYES: ("☼", (0x00, 0xBF, 0xFF)),
    Suit.SONGS: ("♪", (0x00, 0xD9, 0x00)),
    Suit.STORMS: ("≈", (0x80, 0x00, 0xFF)),
}
