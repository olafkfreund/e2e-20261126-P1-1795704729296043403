# AC#3: return 2 with non-empty stderr on invalid arguments or missing files.
#
# Covers wordfreq.cli.main for invalid option values (--top -1, --min-len 0,
# non-integer values) and for input paths that do not exist.

import pytest

from wordfreq.cli import main


@pytest.mark.parametrize(
    "argv",
    [
        ["--top", "-1"],
        ["--min-len", "0"],
        ["--top", "abc"],
        ["--min-len", "xyz"],
    ],
    ids=[
        "top_negative_one",
        "min_len_zero",
        "top_non_integer",
        "min_len_non_integer",
    ],
)
def test_main_invalid_argument_returns_exit_code_2(argv, capsys):
    exit_code = main(argv)

    assert exit_code == 2


@pytest.mark.parametrize(
    "argv",
    [
        ["--top", "-1"],
        ["--min-len", "0"],
        ["--top", "abc"],
        ["--min-len", "xyz"],
    ],
    ids=[
        "top_negative_one",
        "min_len_zero",
        "top_non_integer",
        "min_len_non_integer",
    ],
)
def test_main_invalid_argument_writes_non_empty_stderr(argv, capsys):
    main(argv)

    captured = capsys.readouterr()

    assert captured.err.strip() != ""


def test_main_missing_file_returns_exit_code_2(tmp_path, capsys):
    missing = tmp_path / "does_not_exist.txt"

    exit_code = main([str(missing)])

    assert exit_code == 2


def test_main_missing_file_writes_non_empty_stderr(tmp_path, capsys):
    missing = tmp_path / "does_not_exist.txt"

    main([str(missing)])

    captured = capsys.readouterr()

    assert captured.err.strip() != ""
