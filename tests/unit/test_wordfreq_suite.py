# Criterion (AC#4, subtask wordfreq-suite-tie-breaking-end-to-end):
# "pytest -q passes across tests/test_wordfreq.py" -- end-to-end tie-breaking and
# ranked output through main. Words are sorted by (-count, word); main honors
# --top, --min-len, --case-sensitive and --json; TSV and --json output end with
# a final "\n"; empty TSV output writes nothing.

import io
import json
import sys

import pytest

from wordfreq.cli import main


@pytest.fixture
def stdin_text(monkeypatch):
    def _set(text):
        monkeypatch.setattr(sys, "stdin", io.StringIO(text))

    return _set


def test_main_equal_counts_tie_broken_alphabetically(stdin_text, capsys):
    stdin_text("b a c a b c")
    main([])
    out = capsys.readouterr().out
    assert out == "a\t2\nb\t2\nc\t2\n"


def test_main_mixed_counts_ranked_by_count_then_word(stdin_text, capsys):
    stdin_text("zebra apple apple mango mango mango")
    main([])
    out = capsys.readouterr().out
    assert out == "mango\t3\napple\t2\nzebra\t1\n"


def test_main_tie_at_top_cutoff_keeps_alphabetical_order(stdin_text, capsys):
    stdin_text("b a c a b c d")
    main(["--top", "2"])
    out = capsys.readouterr().out
    assert out == "a\t2\nb\t2\n"


def test_main_default_case_folding_merges_tied_words(stdin_text, capsys):
    stdin_text("Apple apple")
    main([])
    out = capsys.readouterr().out
    assert out == "apple\t2\n"


def test_main_case_sensitive_tie_orders_uppercase_first(stdin_text, capsys):
    stdin_text("Apple apple")
    main(["--case-sensitive"])
    out = capsys.readouterr().out
    assert out == "Apple\t1\napple\t1\n"


def test_main_min_len_filters_then_ties_alphabetical(stdin_text, capsys):
    stdin_text("aa bb a b cc")
    main(["--min-len", "2"])
    out = capsys.readouterr().out
    assert out == "aa\t1\nbb\t1\ncc\t1\n"


def test_main_tsv_output_ends_with_single_newline(stdin_text, capsys):
    stdin_text("x y x")
    main([])
    out = capsys.readouterr().out
    assert out.endswith("\n") and not out.endswith("\n\n")


def test_main_empty_tsv_output_writes_nothing(stdin_text, capsys):
    stdin_text("")
    main([])
    out = capsys.readouterr().out
    assert out == ""


def test_main_json_output_ends_with_newline(stdin_text, capsys):
    stdin_text("b a c a b c")
    main(["--json"])
    out = capsys.readouterr().out
    assert out.endswith("\n")


def test_main_json_output_is_valid_json(stdin_text, capsys):
    stdin_text("b a c a b c")
    main(["--json"])
    out = capsys.readouterr().out
    assert json.loads(out) is not None


def test_main_repeated_tied_input_output_is_deterministic(stdin_text, capsys):
    stdin_text("d c b a d c b a")
    main([])
    first = capsys.readouterr().out
    stdin_text("d c b a d c b a")
    main([])
    second = capsys.readouterr().out
    assert first == second == "a\t2\nb\t2\nc\t2\nd\t2\n"


def test_main_dash_path_reads_stdin_tie_broken(stdin_text, capsys):
    stdin_text("b a b a")
    main(["-"])
    out = capsys.readouterr().out
    assert out == "a\t2\nb\t2\n"
