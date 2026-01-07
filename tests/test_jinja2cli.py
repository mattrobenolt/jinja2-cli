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


class TestDeepMerge:
    """Test the deep_merge function"""

    def test_merge_simple_values(self):
        """Test merging simple key-value pairs"""
        target = {"a": 1, "b": 2}
        source = {"c": 3}
        result = cli.deep_merge(target, source)
        assert result == {"a": 1, "b": 2, "c": 3}
        assert result is target  # Should modify in place

    def test_merge_nested_dicts(self):
        """Test merging nested dictionaries"""
        target = {"server": {"host": "localhost", "timeout": 30}}
        source = {"server": {"port": 8080}}
        result = cli.deep_merge(target, source)
        assert result == {"server": {"host": "localhost", "timeout": 30, "port": 8080}}

    def test_merge_multiple_levels_deep(self):
        """Test merging multiple levels deep"""
        target = {"a": {"b": {"c": 1, "d": 2}}}
        source = {"a": {"b": {"e": 3}}}
        result = cli.deep_merge(target, source)
        assert result == {"a": {"b": {"c": 1, "d": 2, "e": 3}}}

    def test_merge_override_leaf_values(self):
        """Test that leaf values are overridden"""
        target = {"server": {"host": "localhost", "port": 3000}}
        source = {"server": {"port": 8080}}
        result = cli.deep_merge(target, source)
        assert result == {"server": {"host": "localhost", "port": 8080}}

    def test_merge_dict_over_non_dict(self):
        """Test merging dict over non-dict value (dict wins)"""
        target = {"server": "old_value"}
        source = {"server": {"host": "localhost"}}
        result = cli.deep_merge(target, source)
        assert result == {"server": {"host": "localhost"}}

    def test_merge_non_dict_over_dict(self):
        """Test merging non-dict over dict value (non-dict wins)"""
        target = {"server": {"host": "localhost"}}
        source = {"server": "new_value"}
        result = cli.deep_merge(target, source)
        assert result == {"server": "new_value"}

    def test_merge_empty_source(self):
        """Test merging empty source dict"""
        target = {"a": 1, "b": {"c": 2}}
        source = {}
        result = cli.deep_merge(target, source)
        assert result == {"a": 1, "b": {"c": 2}}

    def test_merge_empty_target(self):
        """Test merging into empty target dict"""
        target = {}
        source = {"a": 1, "b": {"c": 2}}
        result = cli.deep_merge(target, source)
        assert result == {"a": 1, "b": {"c": 2}}

    def test_merge_complex_nested_structure(self):
        """Test merging complex nested structure with multiple branches"""
        target = {
            "database": {"host": "localhost", "port": 5432},
            "cache": {"redis": {"host": "redis-host"}},
            "debug": True,
        }
        source = {
            "database": {"user": "admin"},
            "cache": {"redis": {"port": 6379}, "ttl": 300},
            "logging": {"level": "info"},
        }
        result = cli.deep_merge(target, source)
        assert result == {
            "database": {"host": "localhost", "port": 5432, "user": "admin"},
            "cache": {"redis": {"host": "redis-host", "port": 6379}, "ttl": 300},
            "debug": True,
            "logging": {"level": "info"},
        }

    def test_merge_preserves_sibling_values(self):
        """Test that merging preserves sibling values at all levels"""
        target = {"a": {"b": 1, "c": 2}, "d": 3}
        source = {"a": {"c": 99}}
        result = cli.deep_merge(target, source)
        assert result == {"a": {"b": 1, "c": 99}, "d": 3}

    def test_merge_with_none_values(self):
        """Test merging with None values"""
        target = {"a": 1, "b": None}
        source = {"b": 2, "c": None}
        result = cli.deep_merge(target, source)
        assert result == {"a": 1, "b": 2, "c": None}

    def test_merge_with_list_values(self):
        """Test merging with list values (lists are replaced, not merged)"""
        target = {"items": [1, 2, 3]}
        source = {"items": [4, 5]}
        result = cli.deep_merge(target, source)
        assert result == {"items": [4, 5]}


class TestParseKvString:
    """Test the parse_kv_string function"""

    def test_simple_key_value(self):
        """Test simple key=value pairs"""
        result = cli.parse_kv_string(["foo=bar", "baz=qux"])
        assert result == {"foo": "bar", "baz": "qux"}

    def test_dot_notation_single_level(self):
        """Test dot notation with single level nesting"""
        result = cli.parse_kv_string(["foo.bar=baz"])
        assert result == {"foo": {"bar": "baz"}}

    def test_dot_notation_multiple_levels(self):
        """Test dot notation with multiple levels"""
        result = cli.parse_kv_string(["a.b.c=value"])
        assert result == {"a": {"b": {"c": "value"}}}

    def test_dot_notation_multiple_keys(self):
        """Test multiple keys with dot notation"""
        result = cli.parse_kv_string(["server.host=localhost", "server.port=8080"])
        assert result == {"server": {"host": "localhost", "port": "8080"}}

    def test_mixed_notation(self):
        """Test mix of simple and dot notation"""
        result = cli.parse_kv_string(["simple=value", "nested.key=value2"])
        assert result == {"simple": "value", "nested": {"key": "value2"}}

    def test_dot_notation_override(self):
        """Test that later values override earlier ones"""
        result = cli.parse_kv_string(["foo.bar=first", "foo.bar=second"])
        assert result == {"foo": {"bar": "second"}}

    def test_key_without_value(self):
        """Test key without value (edge case)"""
        result = cli.parse_kv_string(["foo"])
        assert result == {"foo": None}

    def test_dot_notation_with_existing_path(self):
        """Test adding to existing nested path"""
        result = cli.parse_kv_string(["foo.bar=1", "foo.baz=2"])
        assert result == {"foo": {"bar": "1", "baz": "2"}}
