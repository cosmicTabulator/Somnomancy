from enum import auto, Enum

class Directions(Enum):

    N = 0
    E = 1
    S = 2
    W = 3

    def rot(self, times=1):
        return Directions((self.value + times) % 4)

    def flip(self):
        return self.rot(times=2)

    def to_delta(self):
        if self.value == 0:
            return (0, -1)
        elif self.value == 1:
            return (1, 0)
        elif self.value == 2:
            return (0, 1)
        else:
            return (-1, 0)
