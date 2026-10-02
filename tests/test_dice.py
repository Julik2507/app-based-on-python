from unittest.mock import MagicMock

from practice.dice import Dice, play_two_dice


def test_play_two_dice_sums_both_throws():
    dice = MagicMock(spec=Dice)
    dice.throw.side_effect = [3, 5]

    assert play_two_dice(dice) == 8
    assert dice.throw.call_count == 2


def test_play_two_dice_double_six():
    dice = MagicMock(spec=Dice)
    dice.throw.return_value = 6

    assert play_two_dice(dice) == 12
