import os
import json
import subprocess

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


def test_cmd_succeeds():
    template = "files/maindir_template.j2"
    title = "Greatest Title 1"
    ctx = json.dumps({"title": title})
    echo_proc = subprocess.Popen(["echo", ctx], stdout=subprocess.PIPE, shell=False)
    jinja_proc = subprocess.Popen(
        ["jinja2", template],
        stdin=echo_proc.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
    )
    assert jinja_proc.wait() == 0
    assert jinja_proc.stderr.readlines() == []
    assert jinja_proc.stdout.readlines() == [(title + "\n").encode()]


def test_cmd_fails_without_includes_flag():
    template = "files/subdir/subdir_template.j2"
    title = "Greatest Title 2"
    context = json.dumps({"title": title})
    echo_args = ["echo", context]
    jinja_args = ["jinja2", template]
    echo_proc = subprocess.Popen(echo_args, stdout=subprocess.PIPE, shell=False)
    jinja_proc = subprocess.Popen(
        jinja_args,
        stdin=echo_proc.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
    )
    assert jinja_proc.wait() == 1
    jinja_err = jinja_proc.stderr.readlines()
    assert "jinja2.exceptions.TemplateNotFound" in jinja_err[-1].decode("utf-8")
    assert jinja_proc.stdout.readlines() == []


def test_cmd_succeeds_with_includes_flag():
    template = "files/subdir/subdir_template.j2"
    title = "Greatest Title 3"
    ctx = json.dumps({"title": title})
    template_root = "files"
    echo_args = ["echo", ctx]
    jinja_args = ["jinja2", template, "--includes", template_root]
    echo_proc = subprocess.Popen(echo_args, stdout=subprocess.PIPE, shell=False)
    jinja_proc = subprocess.Popen(
        jinja_args,
        stdin=echo_proc.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
    )
    assert jinja_proc.wait() == 0
    assert jinja_proc.stderr.readlines() == []
    assert jinja_proc.stdout.readlines() == [(title + "\n").encode()]
