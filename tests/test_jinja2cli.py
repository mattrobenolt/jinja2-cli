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


def test_non_recursive():
    path = "./files/recursive_template.j2"
    data = {'sitename': 'SiteName', 'title': 'Welcome to {{ sitename }}'}
    non_recursive_result_path = "./files/recursive_template_non_recursive_result.html"

    output = cli.render(path, data, [], False, False)
    if isinstance(output, cli.binary_type):
        output = output.decode('utf-8')

    with open(non_recursive_result_path) as f:
        expected_result = f.read()
        assert output == expected_result


def test_recursive():
    path = "./files/recursive_template.j2"
    data = {'sitename': 'SiteName', 'title': 'Welcome to {{ sitename }}'}
    recursive_result_path = "./files/recursive_template_recursive_result.html"

    output = cli.render(path, data, [], False, True)
    if isinstance(output, cli.binary_type):
        output = output.decode('utf-8')

    with open(recursive_result_path) as f:
        expected_result = f.read()
        assert output == expected_result
