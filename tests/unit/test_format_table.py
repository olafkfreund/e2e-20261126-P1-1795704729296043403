# Acceptance criterion (AC#2): format_table formats rows as word\tcount lines
# separated by \n and returns '' for empty input.

from wordfreq.cli import format_table


def test_format_table_two_rows_joined_with_newline_as_word_tab_count():
    rows = [("the", 3), ("fox", 1)]
    assert format_table(rows) == "the\t3\nfox\t1"


def test_format_table_single_row_has_word_tab_count_without_newline():
    rows = [("quick", 7)]
    assert format_table(rows) == "quick\t7"


def test_format_table_rows_use_tab_between_word_and_count():
    rows = [("brown", 2)]
    assert format_table(rows) == "brown\t2"


def test_format_table_empty_input_returns_empty_string():
    assert format_table([]) == ""
