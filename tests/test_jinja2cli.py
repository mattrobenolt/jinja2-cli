import os

import pytest

from jinja2cli import cli

# change dir to tests directory to make relative paths possible
os.chdir(os.path.dirname(os.path.realpath(__file__)))


def test_relative_path():
    path = "./files/template.j2"

    title = b"\xc3\xb8".decode("utf8")
    output = cli.render(path, {"title": title}, [])
    assert output == title
    assert isinstance(output, str)


def test_absolute_path():
    absolute_base_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(absolute_base_path, "files", "template.j2")

    title = b"\xc3\xb8".decode("utf8")
    output = cli.render(path, {"title": title}, [])
    assert output == title
    assert isinstance(output, str)


class TestDiscoverFilters:
    """Test the discover_filters function"""

    def test_discover_single_function(self):
        """Test discovering a single filter function"""
        base_dir = os.path.dirname(os.path.realpath(__file__))
        filters = cli.discover_filters("fixtures.filters.custom.reverse", base_dir)

        assert "reverse" in filters
        assert callable(filters["reverse"])
        assert filters["reverse"]("hello") == "olleh"

    def test_discover_multiple_functions(self):
        """Test discovering multiple filter functions via filters dict"""
        base_dir = os.path.dirname(os.path.realpath(__file__))
        filters = cli.discover_filters("fixtures.filters.custom.filters", base_dir)

        assert "reverse" in filters
        assert "multiply" in filters
        assert "shout" in filters
        assert filters["reverse"]("hello") == "olleh"
        assert filters["multiply"](5, 3) == 15
        assert filters["shout"]("hi") == "HI!"

    def test_autodiscover_module(self):
        """Test auto-discovering all functions from a module"""
        base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures/filters")
        filters = cli.discover_filters("autodiscover", base_dir)

        assert "uppercase" in filters
        assert "lowercase" in filters
        assert "double" in filters
        assert "_private_function" not in filters  # Should skip private functions

        assert filters["uppercase"]("hello") == "HELLO"
        assert filters["lowercase"]("HELLO") == "hello"
        assert filters["double"](5) == 10

    def test_discover_module_with_filters_dict(self):
        """Test discovering filters from a module with a filters dict"""
        base_dir = os.path.dirname(os.path.realpath(__file__))
        filters = cli.discover_filters("fixtures.filters.custom", base_dir)

        assert "reverse" in filters
        assert "multiply" in filters
        assert "shout" in filters

    def test_discover_loader_function(self):
        """Test discovering filters via a load_ function"""
        base_dir = os.path.dirname(os.path.realpath(__file__))
        filters = cli.discover_filters(
            "fixtures.filters.ansible_helper.load_core_filters", base_dir
        )

        # Should have loaded filters (or empty dict if ansible not installed)
        assert isinstance(filters, dict)

    def test_discover_nonexistent_module(self):
        """Test that discovering from nonexistent module raises error"""
        with pytest.raises(ModuleNotFoundError):
            cli.discover_filters("nonexistent.module")

    def test_discover_nonexistent_attribute(self):
        """Test that discovering nonexistent attribute raises error"""
        base_dir = os.path.dirname(os.path.realpath(__file__))
        with pytest.raises(ModuleNotFoundError):
            cli.discover_filters("fixtures.filters.custom.nonexistent", base_dir)
