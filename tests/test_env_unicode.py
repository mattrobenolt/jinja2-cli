import subprocess
import sys
import warnings

import pytest

from jinja2cli.cli import parse_env


@pytest.mark.parametrize("value", ["café", "中文 日本語 한국어", "😀", "e\u0301"])
def test_double_quoted_unicode(value):
    assert parse_env(f'NAME="{value}"') == {"NAME": value}


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (r"café\n中文\t😀", "café\n中文\t😀"),
        (r"中文\"café\"", '中文"café"'),
        (r"中文\\path", "中文\\path"),
        (r"\é", "\\é"),
        (r"\中文", "\\中文"),
        (r"\\中文", "\\中文"),
        (r"\\\中文", "\\\\中文"),
        (r"é\u4e2d\U0001f600\x21\041", "é中😀!!"),
        (r"中文\N{LATIN SMALL LETTER E WITH ACUTE}", "中文é"),
    ],
)
def test_unicode_and_escape_sequences(value, expected):
    assert parse_env(f'NAME="{value}"') == {"NAME": expected}


@pytest.mark.parametrize("quote", ["'", ""])
def test_other_quoting_keeps_unicode_and_backslashes(quote):
    value = r"café\n中文\u4e2d"
    assert parse_env(f"NAME={quote}{value}{quote}") == {"NAME": value}


def test_unknown_ascii_escape_is_preserved_with_warning():
    with pytest.warns((DeprecationWarning, SyntaxWarning), match="invalid escape sequence"):
        assert parse_env(r'NAME="\q"') == {"NAME": r"\q"}


@pytest.mark.parametrize("value", [r"\x1", r"\u123", r"\U00110000", r"\N{INVALID}", "tail\\"])
def test_malformed_escape_still_raises(value):
    with pytest.raises(UnicodeDecodeError):
        parse_env(f'NAME="{value}"')


@pytest.mark.parametrize("value", ["\\q\\", "\\qé\\", "中文\\q😀\\", "\\qé\\u123"])
def test_trailing_backslash_error_precedes_unknown_escape_warning(value):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        with pytest.raises(UnicodeDecodeError):
            parse_env(f'NAME="{value}"')


def test_env_unicode_cli(tmp_path):
    template = tmp_path / "template.j2"
    data = tmp_path / "data.env"
    template.write_text("{{ NAME }}", encoding="utf-8")
    data.write_text('NAME="café\\n中文 😀"', encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "-X",
            "utf8",
            "-m",
            "jinja2cli.cli",
            str(template),
            str(data),
            "--format=env",
        ],
        capture_output=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == "café\n中文 😀"
