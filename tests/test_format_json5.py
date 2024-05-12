#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from jinja2cli import cli


Json5ParserFn, Json5ExpectException, Json5RaiseException = cli.get_format("json5")


@pytest.mark.parametrize(
    ("json5", "expected"),
    [
        ("{}", {}),
        (
            "{  // comments\n  "
            "unquoted: 'and you can quote me on that',\n  "
            "singleQuotes: 'I can use \"double quotes\" here',\n  "
            "hexadecimal: 0xdecaf,\n  "
            "leadingDecimalPoint: .8675309, andTrailing: 8675309.,\n  "
            "positiveSign: +1,\n  "
            "trailingComma: 'in objects', andIn: ['arrays',],\n  "
            "\"backwardsCompatible\": \"with JSON\",\n"
            "}\n",
            {
                "unquoted": "and you can quote me on that",
                "singleQuotes": 'I can use "double quotes" here',
                "hexadecimal": 0xDECAF,
                "leadingDecimalPoint": 0.8675309,
                "andTrailing": 8675309.0,
                "positiveSign": 1,
                "trailingComma": "in objects",
                "andIn": [
                    "arrays",
                ],
                "backwardsCompatible": "with JSON",
            },
        ),
        pytest.param(
            '{foo: "bar\nham"}',
            {"foo": "bar\nham"},
            marks=pytest.mark.skip(
                reason="json5 package doesn't support line breaks in values, may change in the future since hjson"
            ),
        ),
    ],
)
def test_json5(json5, expected):
    assert Json5ParserFn(json5) == expected


@pytest.mark.parametrize(
    ("json5"),
    [
        (""),
    ],
)
def test_json5_errors(json5):
    with pytest.raises(Json5ExpectException):
        Json5ParserFn(json5)
