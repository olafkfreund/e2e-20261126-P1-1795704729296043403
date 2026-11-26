# AC#3: main and `python -m wordfreq` read from stdin, return 0 or 2 with stderr.
# Verify running `python -m wordfreq` as a subprocess reads stdin, emits
# JSON/TSV with a trailing newline, and exits 2 with stderr on a missing file.

import os
import subprocess
import sys

import pytest

import wordfreq

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(wordfreq.__file__)))


def _run_wordfreq(args, stdin_text=None):
    return subprocess.run(
        [sys.executable, "-m", "wordfreq", *args],
        input=stdin_text,
        capture_output=True,
        text=True,
        timeout=30,
        cwd=_PROJECT_ROOT,
    )


@pytest.fixture
def stdin_text():
    return "the quick brown fox jumps over the lazy dog the end\n"


def test_python_m_wordfreq_stdin_exit_code_zero(stdin_text):
    result = _run_wordfreq([], stdin_text=stdin_text)
    assert result.returncode == 0


def test_python_m_wordfreq_stdin_emits_output(stdin_text):
    result = _run_wordfreq([], stdin_text=stdin_text)
    assert result.stdout.strip() != ""


def test_python_m_wordfreq_stdin_output_ends_with_trailing_newline(stdin_text):
    result = _run_wordfreq([], stdin_text=stdin_text)
    assert result.stdout.endswith("\n")


def test_python_m_wordfreq_missing_file_exit_code_two(tmp_path):
    missing = tmp_path / "does_not_exist.txt"
    result = _run_wordfreq([str(missing)])
    assert result.returncode == 2


def test_python_m_wordfreq_missing_file_writes_stderr(tmp_path):
    missing = tmp_path / "does_not_exist.txt"
    result = _run_wordfreq([str(missing)])
    assert result.stderr.strip() != ""
