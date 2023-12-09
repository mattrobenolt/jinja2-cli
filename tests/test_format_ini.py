#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from jinja2cli import cli
from .common import is_python_version

IIinParserFn, IniExpectException, IniRaiseException = cli.get_format("ini")


@pytest.mark.xfail(
    is_python_version(3, 12),
    strict=True,
    raises=AttributeError,
    reason="Jinja2cli uses `configparser.ConfigParser.readfp` that is deprecated in Python3.12",
)
@pytest.mark.parametrize(
    ("ini", "ini_data"),
    [
        ("", {}),
        ("[data]\nfoo=bar", {"data": {"foo": "bar"}}),
        ("[data]\nfoo=bar\nham=spam", {"data": {"foo": "bar", "ham": "spam"}}),
        (
            "[data1]\nfoo=bar\n[data2]\nham=spam",
            {"data1": {"foo": "bar"}, "data2": {"ham": "spam"}},
        ),
        pytest.param(
            "[data]\nfoo=bar\n[data]\nham=spam",
            {"data": {"foo": "bar", "ham": "spam"}},
            marks=pytest.mark.skipif(
                not is_python_version(2, 7),
                reason="Duplicate data section names are not supported by configparser in python versions > 2.7",
            ),
        ),
    ],
)
def test_ini(ini, ini_data):
    assert IIinParserFn(ini) == ini_data


@pytest.mark.xfail(
    is_python_version(3, 12),
    strict=True,
    raises=AttributeError,
    reason="Jinja2cli uses `configparser.ConfigParser.readfp` that is deprecated in Python3.12",
)
@pytest.mark.parametrize(
    ("data"),
    [
        ("foo=bar\nham=spam"),
        ("[data]foo=\nbar"),
    ],
)
def test_ini_errors(data):
    with pytest.raises(IniExpectException):
        IIinParserFn(data)
