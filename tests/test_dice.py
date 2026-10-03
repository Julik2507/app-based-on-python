from unittest.mock import MagicMock

from practice import Dice, play_two_dice

def test_play_two_dice():
    dice = MagicMock(spec=Dice)
    dice.throw.side_effect = [3, 5]

    assert play_two_dice() == 8
 

def test_play_two_dice_with_mocked_dice():
    dice = MagicMock(spec=Dice)
    dice.throw.return_value = 6

    assert play_two_dice(dice) == 12