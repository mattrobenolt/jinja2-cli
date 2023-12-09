#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from jinja2cli import cli

XMLParserFn, XMLExpectException, XMLRaiseException = cli.get_format("xml")


@pytest.mark.parametrize(
    ("xml", "xml_data"),
    [
        ("<data></data>", {"data": None}),
        ("<data>foo</data>", {"data": "foo"}),
        ("<data><foo></foo></data>", {"data": {"foo": None}}),
        ("<data><foo>bar</foo></data>", {"data": {"foo": "bar"}}),
        (
            "<data><foo>bar</foo><ham>spam</ham></data>",
            {"data": {"foo": "bar", "ham": "spam"}},
        ),
    ],
)
def test_xml(xml, xml_data):
    assert XMLParserFn(xml) == xml_data


@pytest.mark.parametrize(
    ("data"),
    [
        (""),
        ("<data>"),
        ("</data>"),
        ("<data><data>"),
    ],
)
def test_xml_errors(data):
    with pytest.raises(XMLExpectException):
        XMLParserFn(data)
