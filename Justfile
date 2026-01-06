default:
    @just --list

sync:
    uv sync --all-groups --all-extras

test:
    uv run pytest -v

bats:
    bats tests/bats

test-all: test bats

lint:
    uv run ruff check
    uv run ty check

bench-startup:
    hyperfine --warmup 3 --min-runs 10 ".venv/bin/jinja2 --version"

fmt:
    uv run ruff check --select I --fix
    uv run ruff format

build: clean
    uv build

publish: build
    uv publish

clean:
    rm -rf dist .pytest_cache .ruff_cache
