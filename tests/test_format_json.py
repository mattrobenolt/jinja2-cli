#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pytest

from jinja2cli import cli

JsonParserFn, JsonExpectException, JsonRaiseException = cli.get_format("json")


@pytest.mark.parametrize(
    ("json", "json_data"),
    [
        ("{}", {}),
        ('{"foo": "bar"}', {"foo": "bar"}),
        ('{"": "bar"}', {"": "bar"}),
        ('{"foo": "bar", "ham": "spam"}', {"foo": "bar", "ham": "spam"}),
    ],
)
def test_json(json, json_data):
    assert JsonParserFn(json) == json_data


@pytest.mark.parametrize(
    ("data"),
    [
        (""),
        ('{foo: "bar"}'),
        ('{"foo": bar}'),
    ],
)
def test_json_errors(data):
    with pytest.raises(JsonExpectException):
        JsonParserFn(data)
