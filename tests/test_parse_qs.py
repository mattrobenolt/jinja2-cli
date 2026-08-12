import pytest

from jinja2cli import cli

QS_PARSER_FN, QS_EXCEPT_EXC, QS_RAISE_EXC = cli.get_format("querystring")


@pytest.mark.parametrize(
    ("qs", "qs_data"),
    [
        ("", {}),
        ("foo=", {}),
        ("foo=bar", {"foo": "bar"}),
        ("foo=bar&ham=spam", {"foo": "bar", "ham": "spam"}),
        ("foo.bar=ham&ham.spam=eggs", {"foo": {"bar": "ham"}, "ham": {"spam": "eggs"}}),
        ("foo=bar%20ham%20spam", {"foo": "bar ham spam"}),
        ("foo=bar%2Eham%2Espam", {"foo": "bar.ham.spam"}),
    ],
)
def test_parse_qs(qs, qs_data):
    assert QS_PARSER_FN(qs) == qs_data
