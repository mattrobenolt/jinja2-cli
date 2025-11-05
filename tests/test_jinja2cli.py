import json
import os
from optparse import Values

from jinja2cli import cli

# change dir to tests directory to make relative paths possible
os.chdir(os.path.dirname(os.path.realpath(__file__)))


def expected_output(title, name, items, subtitle, language):
    """Helper to generate expected output for macro tests"""
    lines = [
        f"**{title}**",
        "",
        f"Hello, {name}!",
        "",
    ]
    lines.extend(f"- {item}" for item in items)
    lines.extend(["", f"*{subtitle}*", f"`{language}`"])
    return "\n".join(lines)


# ============================================================================
# Basic Path Resolution Tests
# ============================================================================


def test_relative_path():
    """Verify templates can be loaded using relative paths"""
    path = "./files/template.j2"

    title = b"\xc3\xb8".decode("utf8")
    output = cli.render(path, {"title": title}, [])
    
    assert output == title
    assert type(output) == cli.text_type


def test_absolute_path():
    """Verify templates can be loaded using absolute paths"""
    absolute_base_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(absolute_base_path, "files", "template.j2")

    title = b"\xc3\xb8".decode("utf8")
    output = cli.render(path, {"title": title}, [])
    
    assert output == title
    assert type(output) == cli.text_type


# ============================================================================
# Macro Import Tests (Same Directory)
# ============================================================================


def test_inline_and_imported_macros():
    """Verify templates can use inline macros and import from subdirectories"""
    path = "./files/template_with_macros.j2"

    data = {
        "title": "Test Title",
        "name": "World",
        "items": ["First", "Second", "Third"],
        "subtitle": "A guide",
        "language": "python",
    }

    output = cli.render(path, data, [])
    expected = expected_output(
        data["title"], data["name"], data["items"], data["subtitle"], data["language"]
    )

    assert output.strip() == expected
    assert type(output) == cli.text_type


# ============================================================================
# Relative Import Tests (Parent Directories)
# ============================================================================


def test_parent_directory_import():
    """Verify templates can import from parent directory using ../"""
    path = "./files/nested/child_template.j2"
    
    data = {"name": "World", "message": "Testing parent imports"}
    output = cli.render(path, data, [])
    
    # Should import macros from ../macros_lib/formatting.j2
    expected_lines = ["Hello, World!", "*Testing parent imports*"]
    assert output.strip() == "\n".join(expected_lines)


def test_deep_nested_import():
    """Verify templates can navigate multiple levels using ../../../"""
    path = "./files/deep/level1/level2/deep_template.j2"
    
    data = {"language": "python"}
    output = cli.render(path, data, [])
    
    # Should import macros from ../../../macros_lib/formatting.j2
    expected_lines = ["*Deep nested template*", "`python`"]
    assert output.strip() == "\n".join(expected_lines)


# ============================================================================
# File Output Tests
# ============================================================================


def test_render_to_file(tmp_path):
    """Verify rendering to a file with JSON data input works correctly"""
    template_path = "./files/template_with_macros.j2"

    data = {
        "title": "File Output Test",
        "name": "Jinja2",
        "items": ["One", "Two", "Three"],
        "subtitle": "Template",
        "language": "cli",
    }

    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(data))

    outfile = tmp_path / "output.txt"

    opts = Values(
        {
            "format": "json",
            "extensions": set(["do", "loopcontrols"]),
            "D": None,
            "section": None,
            "strict": False,
            "outfile": str(outfile),
        }
    )

    args = [os.path.abspath(template_path), str(data_file)]
    result = cli.cli(opts, args)

    assert result == 0

    output = outfile.read_text().strip()
    expected = expected_output(
        data["title"], data["name"], data["items"], data["subtitle"], data["language"]
    )
    assert output == expected

