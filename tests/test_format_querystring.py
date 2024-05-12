#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from jinja2cli import cli

QSParserFn, QSExpectException, QSRaiseException = cli.get_format("querystring")


@pytest.mark.parametrize(
    ("qs", "expected"),
    [
        ("", {}),
        ("foo=bar", {"foo": "bar"}),
        ("foo=", {}),
        ("foo=bar&ham=spam", {"foo": "bar", "ham": "spam"}),
        (
            "foo.bar=ham&ham.spam=eggs",
            {"foo": {"bar": "ham"}, "ham": {"spam": "eggs"}},
        ),
        ("foo=bar%20ham%20spam", {"foo": "bar ham spam"}),
        ("foo=bar%2Eham%2Espam", {"foo": "bar.ham.spam"}),
        (
            "foo.bar.ham=spam&foo.bar.spam=eggs",
            {"foo": {"bar": {"ham": "spam", "spam": "eggs"}}},
        ),
        (
            "foo.bar.ham=spam&foo.baz.ham=spam",
            {"foo": {"bar": {"ham": "spam"}, "baz": {"ham": "spam"}}},
        ),
    ],
)
def test_qs(qs, expected):
    assert expected == QSParserFn(qs)
