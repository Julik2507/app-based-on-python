import random


class Dice:
    def throw(self) -> int:
        return random.randint(1, 6)


def play_two_dice(dice: Dice) -> int:
    return dice.throw() + dice.throw()
