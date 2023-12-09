#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from jinja2cli import cli

EnvParserFn, EnvExpectException, EnvRaiseException = cli.get_format("env")


@pytest.mark.parametrize(
    ("env", "env_data"),
    [
        ("", {}),
        ("foo=bar", {"foo": "bar"}),
        ("foo=", {"foo": ""}),
        ("foo=bar\nham=spam", {"foo": "bar", "ham": "spam"}),
    ],
)
def test_env(env, env_data):
    assert EnvParserFn(env) == env_data


def test_env_multiline_value():
    with pytest.raises(EnvExpectException):
        EnvParserFn("foo=bar\nham\nspam")
