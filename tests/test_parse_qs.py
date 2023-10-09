import pytest

from jinja2cli import cli

QS_PARSER_FN, QS_EXCEPT_EXC, QS_RAISE_EXC = cli.get_format("querystring")


@pytest.mark.parametrize(
    ("qs", "qs_data"),
    [
        ("", dict()),
        ("foo=", dict()),
        ("foo=bar", dict(foo="bar")),
        ("foo=bar&ham=spam", dict(foo="bar", ham="spam")),
        ("foo.bar=ham&ham.spam=eggs", dict(foo=dict(bar="ham"), ham=dict(spam="eggs"))),
        ("foo=bar%20ham%20spam", dict(foo="bar ham spam")),
        ("foo=bar%2Eham%2Espam", dict(foo="bar.ham.spam")),
    ],
)
def test_parse_qs(qs, qs_data):
    assert QS_PARSER_FN(qs) == qs_data
