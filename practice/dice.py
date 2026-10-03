class Dice:
    def throw(self) -> int:
        import random
        return random.randint(1, 6)

def play_two_dice() -> int:
    dice1 = Dice()
    dice2 = Dice()
    return dice1.throw() + dice2.throw()