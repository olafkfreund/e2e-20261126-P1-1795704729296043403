"""Unit and CLI tests for the wordfreq package."""

from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from wordfreq.cli import count_words, format_table, main

if TYPE_CHECKING:
    from collections.abc import Sequence

ROOT = Path(__file__).resolve().parents[1]


def _run_module(
    args: Sequence[str] = (), stdin: str = ""
) -> subprocess.CompletedProcess[str]:
    """Run `python -m wordfreq` in a subprocess from the repository root."""
    return subprocess.run(
        [sys.executable, "-m", "wordfreq", *args],
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=ROOT,
        check=False,
    )


def test_count_words_basic_ranking() -> None:
    text = "Apple banana apple, cherry! Banana apple."
    assert count_words(text) == [("apple", 3), ("banana", 2), ("cherry", 1)]


def test_format_table_tsv() -> None:
    assert format_table([("apple", 3), ("banana", 2)]) == "apple\t3\nbanana\t2"


def test_cli_top_and_min_len(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("to be or not to be that is the question", encoding="utf-8")
    rc = main([str(sample), "--min-len", "3", "--top", "2"])
    assert rc == 0
    out = capsys.readouterr().out
    assert out.strip().splitlines() == ["not\t1", "question\t1"]


# Tie-breaking: equal counts are ordered alphabetically by word.


def test_count_words_breaks_ties_alphabetically() -> None:
    text = "pear apple mango apple pear mango kiwi"
    assert count_words(text) == [("apple", 2), ("mango", 2), ("pear", 2), ("kiwi", 1)]


def test_count_words_tie_order_ignores_first_seen_position() -> None:
    assert count_words("zebra apple") == [("apple", 1), ("zebra", 1)]


def test_count_words_top_truncates_after_tie_break() -> None:
    assert count_words("c b a", top=2) == [("a", 1), ("b", 1)]


def test_format_table_empty_input_returns_empty_string() -> None:
    assert format_table([]) == ""


# Case handling.


def test_count_words_lowercases_by_default() -> None:
    assert count_words("Apple apple APPLE") == [("apple", 3)]


def test_count_words_case_sensitive_keeps_spellings_separate() -> None:
    assert count_words("Apple apple APPLE apple", ignore_case=False) == [
        ("apple", 2),
        ("APPLE", 1),
        ("Apple", 1),
    ]


def test_cli_case_sensitive_flag_keeps_spellings_separate(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("Apple apple", encoding="utf-8")
    assert main([str(sample), "--case-sensitive"]) == 0
    assert capsys.readouterr().out == "Apple\t1\napple\t1\n"


def test_cli_default_lowercases_spellings(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("Apple apple", encoding="utf-8")
    assert main([str(sample)]) == 0
    assert capsys.readouterr().out == "apple\t2\n"


# Argument validation.


def test_count_words_rejects_min_len_below_one() -> None:
    with pytest.raises(ValueError, match=r"^min_len must be >= 1$"):
        count_words("text", min_len=0)


def test_count_words_rejects_negative_top() -> None:
    with pytest.raises(ValueError, match=r"^top must be >= 0$"):
        count_words("text", top=-1)


def test_count_words_top_zero_returns_no_rows() -> None:
    assert count_words("a b", top=0) == []


@pytest.mark.parametrize(
    "args",
    [
        ["--top", "-1"],
        ["--top", "abc"],
        ["--min-len", "0"],
        ["--min-len", "x"],
        ["--unknown-flag"],
    ],
)
def test_cli_rejects_invalid_arguments_with_exit_code_2(
    args: list[str],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("apple"))
    assert main(args) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""


# Default stdin input.


@pytest.mark.parametrize("args", [[], ["-"]])
def test_cli_reads_stdin_by_default_or_with_dash(
    args: list[str],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("Beta alpha beta\n"))
    assert main(args) == 0
    assert capsys.readouterr().out == "beta\t2\nalpha\t1\n"


# Trailing newlines on TSV and --json output.


def test_cli_tsv_output_ends_with_single_newline(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("apple banana apple", encoding="utf-8")
    assert main([str(sample)]) == 0
    assert capsys.readouterr().out == "apple\t2\nbanana\t1\n"


def test_cli_empty_tsv_output_prints_nothing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("!!! ... ???"))
    assert main([]) == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_cli_top_zero_prints_nothing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("apple banana"))
    assert main(["--top", "0"]) == 0
    assert capsys.readouterr().out == ""


def test_cli_json_output_is_array_with_trailing_newline(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("apple banana apple"))
    assert main(["--json"]) == 0
    out = capsys.readouterr().out
    assert out.endswith("\n")
    assert json.loads(out) == [
        {"word": "apple", "count": 2},
        {"word": "banana", "count": 1},
    ]


def test_cli_json_empty_input_prints_empty_array(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("!!!"))
    assert main(["--json"]) == 0
    assert capsys.readouterr().out == "[]\n"


# Missing-file handling.


def test_cli_missing_file_returns_2_with_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_path / "missing.txt"
    assert main([str(missing)]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "missing.txt" in captured.err


# `python -m wordfreq` entry point.


def test_python_m_wordfreq_reads_stdin_and_prints_tsv() -> None:
    result = _run_module(stdin="apple banana apple\n")
    assert result.returncode == 0
    assert result.stdout == "apple\t2\nbanana\t1\n"
    assert result.stderr == ""


def test_python_m_wordfreq_json_output_ends_with_newline() -> None:
    result = _run_module(["--json"], stdin="apple banana apple\n")
    assert result.returncode == 0
    assert result.stdout.endswith("\n")
    assert json.loads(result.stdout) == [
        {"word": "apple", "count": 2},
        {"word": "banana", "count": 1},
    ]


def test_python_m_wordfreq_reads_file_argument(tmp_path: Path) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("Apple apple", encoding="utf-8")
    result = _run_module([str(sample), "--case-sensitive"])
    assert result.returncode == 0
    assert result.stdout == "Apple\t1\napple\t1\n"


def test_python_m_wordfreq_missing_file_exits_2(tmp_path: Path) -> None:
    result = _run_module([str(tmp_path / "missing.txt")])
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr.strip() != ""


def test_python_m_wordfreq_invalid_argument_exits_2() -> None:
    result = _run_module(["--min-len", "0"])
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr.strip() != ""
