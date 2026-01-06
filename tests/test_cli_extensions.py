import os
import subprocess
import sys
from pathlib import Path


def _run_cli(args, cwd):
    env = os.environ.copy()
    repo_root = Path(__file__).resolve().parents[1]
    pythonpath = [str(repo_root)]
    if env.get("PYTHONPATH"):
        pythonpath.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(pythonpath)
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
