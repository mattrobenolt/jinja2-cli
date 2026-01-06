import pytest

from jinja2cli import cli


def _get_parser(fmt):
    if not cli.has_format(fmt):
        pytest.skip(f"{fmt} format not available")
    parser, _, _ = cli.get_format(fmt)
    return parser


def test_json_format():
    parser = _get_parser("json")
    assert parser('{"foo": "bar"}') == {"foo": "bar"}


def test_ini_format():
    parser = _get_parser("ini")
    data = parser("[section]\nfoo=bar\n")
    assert data == {"section": {"foo": "bar"}}


def test_yaml_format():
    parser = _get_parser("yaml")
    assert parser("foo: bar\n") == {"foo": "bar"}


def test_toml_format():
    parser = _get_parser("toml")
    assert parser('foo = "bar"\n') == {"foo": "bar"}


def test_xml_format():
    parser = _get_parser("xml")
    assert parser("<root><foo>bar</foo></root>") == {"root": {"foo": "bar"}}


def test_env_format():
    parser = _get_parser("env")
    assert parser("FOO=bar\nBAR=baz\n") == {"FOO": "bar", "BAR": "baz"}


def test_hjson_format():
    parser = _get_parser("hjson")
    assert parser("foo: bar\n") == {"foo": "bar"}


def test_json5_format():
    parser = _get_parser("json5")
    assert parser("{foo: 'bar',}") == {"foo": "bar"}
