import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _pythonpath_env():
    env = os.environ.copy()
    pythonpath = [str(REPO_ROOT)]
    if env.get("PYTHONPATH"):
        pythonpath.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(pythonpath)
    return env


def _run_cli(args, cwd):
    env = _pythonpath_env()
    return subprocess.run(
        [sys.executable, "-m", "jinja2cli.cli", *args],
        cwd=cwd,
        env=env,
        check=True,
        text=True,
        capture_output=True,
    )


def test_local_extension_from_cwd(tmp_path):
    extension = tmp_path / "myext.py"
    extension.write_text(
        "\n".join(
            [
                "from jinja2.ext import Extension",
                "",
                "class ShoutExtension(Extension):",
                "    def __init__(self, environment):",
                "        super().__init__(environment)",
                "        environment.filters['shout'] = lambda value: str(value).upper()",
            ]
        ),
        encoding="utf8",
    )
    template = tmp_path / "template.j2"
    template.write_text("{{ name|shout }}", encoding="utf8")
    data = tmp_path / "data.json"
    data.write_text('{"name": "matt"}', encoding="utf8")

    result = _run_cli(
        [
            str(template),
            str(data),
            "--format",
            "json",
            "-e",
            "myext:ShoutExtension",
        ],
        cwd=tmp_path,
    )

    assert result.stdout == "MATT"


def test_python_dash_m_jinja2cli(tmp_path):
    template = tmp_path / "template.j2"
    template.write_text("{{ name }}", encoding="utf8")
    data = tmp_path / "data.json"
    data.write_text('{"name": "matt"}', encoding="utf8")

    result = subprocess.run(
        [sys.executable, "-m", "jinja2cli", str(template), str(data), "--format", "json"],
        cwd=tmp_path,
        env=_pythonpath_env(),
        check=True,
        text=True,
        capture_output=True,
    )

    assert result.stdout == "matt"
