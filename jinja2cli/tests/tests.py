import os
from jinja2cli import cli

# change dir to tests directory to make relative paths possible
os.chdir(os.path.dirname(os.path.realpath(__file__)))


def relative_path_test():
    path = "./files/template.j2"

    output = cli.render(path, {"title": "Test"})
    assert output == "Test"


def absolute_path_test():
    absolute_base_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(absolute_base_path, "files", "template.j2")

    output = cli.render(path, {"title": "Test"})
    assert output == "Test"
