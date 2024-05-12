#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from jinja2cli import cli
from .common import is_python_version

try:
    HJsonParserFn, HJsonExpectException, HJsonRaiseException = cli.get_format(
        "hjson"
    )
except cli.InvalidDataFormat:
    HJsonParserFn = lambda x: x
    HJsonExpectException = BaseException
    HJsonRaiseException = BaseException


HJSON_STR = """{
    // use #, // or /**/ comments,
    // omit quotes for keys
    key: 1
    // omit quotes for strings
    contains: everything on this line
    // omit commas at the end of a line
    cool: {
        foo: 1
        bar: 2
    }
    // allow trailing commas
    list: [
        1,
        2,
    ]
    // and use multiline strings
    realist:
        '''
        My half empty glass,
        I will fill your empty half.
        Now you are half full.
        '''
}
"""

EXPECTED_DATA = {
    "key": 1,
    "contains": "everything on this line",
    "cool": {"foo": 1, "bar": 2},
    "list": [1, 2],
    "realist": "My half empty glass,\nI will fill your empty half.\nNow you are half full.",
}


@pytest.mark.skipif(
    is_python_version(2, 7),
    reason="there's no hjson package compatible with Python2.7",
)
@pytest.mark.parametrize(
    ("hjson", "expected"),
    [
        ("", {}),
        ("{}", {}),
        (HJSON_STR, EXPECTED_DATA),
    ],
)
def test_hjson(hjson, expected):
    assert HJsonParserFn(hjson) == expected
