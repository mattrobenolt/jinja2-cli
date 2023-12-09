#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from jinja2cli import cli

YamlParserFn, YamlExpectException, YamlRaiseException = cli.get_format("yaml")


@pytest.mark.parametrize(
    ("yaml", "yaml_data"),
    [
        ("", None),
        ("foo", "foo"),
        ("foo: \n", {"foo": None}),
        ("foo: bar", {"foo": "bar"}),
        ("foo: bar\nham: spam", {"foo": "bar", "ham": "spam"}),
        ("foo: |\n bar\n ham\n spam", {"foo": "bar\nham\nspam"}),
        ("foo: >\n bar\n ham\n spam", {"foo": "bar ham spam"}),
        ("foo: \n- bar\n- ham\n- spam", {"foo": ["bar", "ham", "spam"]}),
        ("- foo", ["foo"]),
    ],
)
def test_yaml(yaml, yaml_data):
    assert YamlParserFn(yaml) == yaml_data


@pytest.mark.parametrize(
    ("data"),
    [
        ("foo: \nbar"),
        ("foo: |\nbar"),
    ],
)
def test_yaml_errors(data):
    with pytest.raises(YamlExpectException):
        YamlParserFn(data)
