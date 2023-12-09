#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from jinja2cli import cli

TomlParserFn, TomlExpectException, TomlRaiseException = cli.get_format("toml")


@pytest.mark.parametrize(
    ("toml", "toml_data"),
    [
        ("", {}),
        ("foo=''\n", {"foo": ""}),
        ("foo='bar'\n", {"foo": "bar"}),
        ("''='bar'\n", {"": "bar"}),
    ],
)
def test_toml(toml, toml_data):
    assert TomlParserFn(toml) == toml_data


@pytest.mark.parametrize(
    ("data"),
    [
        ("foo"),
        ("foo=bar\n"),
        ("foo=bar ham=spam\n"),
        ("='bar'\n"),
    ],
)
def test_toml_errors(data):
    with pytest.raises(TomlExpectException):
        TomlParserFn(data)
