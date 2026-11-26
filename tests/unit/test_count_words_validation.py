# AC#1: count_words honours top and raises ValueError('min_len must be >= 1')
# when min_len < 1, or ValueError('top must be >= 0') when top < 0.

import re

import pytest

from wordfreq.cli import count_words


def test_count_words_top_limits_result_length():
    result = count_words("apple apple banana cherry", top=1)
    assert len(result) == 1


@pytest.mark.parametrize(
    "min_len",
    [0, -1, -5],
    ids=["zero", "minus_one", "minus_five"],
)
def test_count_words_min_len_below_one_raises_value_error(min_len):
    with pytest.raises(ValueError, match=re.escape("min_len must be >= 1")):
        count_words("apple banana", min_len=min_len)


@pytest.mark.parametrize(
    "top",
    [-1, -10],
    ids=["minus_one", "minus_ten"],
)
def test_count_words_top_negative_raises_value_error(top):
    with pytest.raises(ValueError, match=re.escape("top must be >= 0")):
        count_words("apple banana", top=top)


def test_count_words_min_len_error_message_is_exact():
    with pytest.raises(ValueError) as exc_info:
        count_words("apple banana", min_len=0)
    assert str(exc_info.value) == "min_len must be >= 1"


def test_count_words_top_error_message_is_exact():
    with pytest.raises(ValueError) as exc_info:
        count_words("apple banana", top=-1)
    assert str(exc_info.value) == "top must be >= 0"
