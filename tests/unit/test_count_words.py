# Criterion (AC#1): count_words extracts [A-Za-z0-9]+ tokens, lowercases by default,
# preserves case when ignore_case=False, filters by min_len, and sorts by (-count, word).

import pytest

from wordfreq.cli import count_words


def test_count_words_extracts_alnum_tokens_splitting_on_other_characters():
    # Underscore and punctuation are not in [A-Za-z0-9], so they act as separators.
    result = dict(count_words("hello, world! foo_bar 42"))

    assert result == {"hello": 1, "world": 1, "foo": 1, "bar": 1, "42": 1}


def test_count_words_default_lowercases_tokens():
    result = dict(count_words("Apple APPLE apple"))

    assert result == {"apple": 3}


@pytest.mark.parametrize(
    "kwargs",
    [
        {"ignore_case": False},
        {"ignore_case": False, "min_len": 1},
    ],
    ids=["ignore_case_false_only", "ignore_case_false_with_min_len"],
)
def test_count_words_ignore_case_false_preserves_case(kwargs):
    result = dict(count_words("Apple APPLE apple", **kwargs))

    assert result == {"Apple": 1, "APPLE": 1, "apple": 1}


def test_count_words_min_len_filters_short_tokens():
    result = dict(count_words("a an the cat is on mat", min_len=3))

    assert result == {"the": 1, "cat": 1, "mat": 1}


def test_count_words_sorts_by_count_descending_then_word_ascending():
    result = list(count_words("pear apple pear banana apple cherry"))

    # apple=2, pear=2 (tie broken alphabetically), banana=1, cherry=1
    assert result == [("apple", 2), ("pear", 2), ("banana", 1), ("cherry", 1)]
