# Criterion (AC#3): main reads stdin by default, honors options, final newline on
# TSV/JSON, nothing for empty TSV.
#
# Subtask: main-stdin-options-output
# Target: wordfreq/cli.py::main

import io
import json

import pytest

from wordfreq.cli import main


@pytest.fixture
def feed_stdin(monkeypatch):
    def _feed(text):
        monkeypatch.setattr("sys.stdin", io.StringIO(text))

    return _feed


def test_main_no_args_reads_stdin_by_default_counts_words(feed_stdin, capsys):
    feed_stdin("apple apple banana\n")

    main([])

    out = capsys.readouterr().out
    assert "apple" in out
    assert "banana" in out


@pytest.mark.parametrize(
    "argv",
    [["-"], ["--top", "10", "-"]],
    ids=["dash-only", "dash-with-top"],
)
def test_main_dash_argument_reads_stdin(feed_stdin, capsys, argv):
    feed_stdin("kiwi kiwi mango\n")

    main(argv)

    out = capsys.readouterr().out
    assert "kiwi" in out
    assert "mango" in out


def test_main_case_sensitive_option_keeps_case_variants_separate(feed_stdin, capsys):
    feed_stdin("The the THE\n")

    main(["--case-sensitive"])

    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 3


def test_main_default_case_folding_merges_case_variants(feed_stdin, capsys):
    feed_stdin("The the THE\n")

    main([])

    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 1


def test_main_top_option_limits_output_to_two_words(feed_stdin, capsys):
    feed_stdin("alpha alpha alpha beta beta gamma delta\n")

    main(["--top", "2"])

    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 2


def test_main_min_len_option_excludes_short_words(feed_stdin, capsys):
    feed_stdin("go go go stop stop run\n")

    main(["--min-len", "3"])

    out = capsys.readouterr().out
    assert "go" not in out
    assert "stop" in out


def test_main_json_option_output_parses_as_json(feed_stdin, capsys):
    feed_stdin("apple apple banana\n")

    main(["--json"])

    out = capsys.readouterr().out
    json.loads(out)


@pytest.mark.parametrize(
    "argv",
    [[], ["--json"]],
    ids=["tsv-default", "json"],
)
def test_main_output_ends_with_final_newline(feed_stdin, capsys, argv):
    feed_stdin("apple apple banana\n")

    main(argv)

    out = capsys.readouterr().out
    assert out.endswith("\n")


def test_main_empty_stdin_tsv_prints_nothing(feed_stdin, capsys):
    feed_stdin("")

    main([])

    assert capsys.readouterr().out == ""
