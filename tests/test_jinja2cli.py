import os

from jinja2cli import cli

# change dir to tests directory to make relative paths possible
os.chdir(os.path.dirname(os.path.realpath(__file__)))


def test_relative_path():
    path = "./files/template.j2"

    title = b"\xc3\xb8".decode("utf8")
    output = cli.render(path, {"title": title}, [])
    assert output == title
    assert type(output) == cli.text_type


def test_absolute_path():
    absolute_base_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(absolute_base_path, "files", "template.j2")

    title = b"\xc3\xb8".decode("utf8")
    output = cli.render(path, {"title": title}, [])
    assert output == title
    assert type(output) == cli.text_type
