from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from game_map import GameMap

class AttackPattern:
    tile_list: List[Tuple[int, int]]

    def __init__(self, x: int, y: int, gamemap: GameMap):
        self.x = x
        self.y = y
        self.tile_list = []

    def get_tile_list(self) -> List[Tuple[int, int]]:
        return self.tile_list

    def is_attack(self, x: int, y: int) -> bool:
        return ((x, y) in self.tile_list)

class AdjacentAttack(AttackPattern):

    def __init__(self, x: int, y: int, radius: int, gamemap: GameMap):
        self.x = x
        self.y = y
        self.tile_list = [(self.x+i, self.y+j) for i, j in range(-radius, radius+1)]
        self.tile_list.pop((self.x, self.y))

class RayAttack(AttackPattern):
    MAX_DISTANCE = 10
    def __init__(self, x: int, y: int, dx: int, dy: int, gamemap: GameMap):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.tile_list = []
        for i in range(self.MAX_DISTANCE):
            tile = (self.x + dx*i, self.y + dy*i)
            if gamemap.tiles[tile[0], tile[1]]["transparent"]:
                self.tile_list.append(tile)
            else:
                break
