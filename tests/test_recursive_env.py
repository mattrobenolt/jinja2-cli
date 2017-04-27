import os
from jinja2cli import cli

# change dir to tests directory to make relative paths possible
os.chdir(os.path.dirname(os.path.realpath(__file__)))


def test_use_plain_file_as_env():
    # For backward capability
    env_file = "./files/test_recursive_env/env/sample.ini"
    data = cli._load_env_from_fs(env_file, False, 'auto')
    assert data == {'main': {'foo': 'bar'}}


def test_use_multiple_files_as_env():
    """
    Verify that we can load environment only in first layer
    """
    env_file = "./files/test_recursive_env/env/"
    data = cli._load_env_from_fs(env_file, False, 'auto')
    assert data == {'main': {'foo': 'bar', 'append': '2'}, 'extra': {'same': '1'}}


def test_use_multiple_files_recursive_as_env():
    """
    Verify that we can load environment recursively
    """
    env_file = "./files/test_recursive_env/env/"
    data = cli._load_env_from_fs(env_file, True, 'auto')
    assert data == {'main': {'foo': 'bar', 'append': '2'},
                    'extra': {'same': '1'}, 'nested': {'delta': '33'}}
