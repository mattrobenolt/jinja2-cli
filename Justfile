[default]
[private]
default:
    @just --list

[doc('Install all dependencies')]
[group('dev')]
sync:
    uv sync --all-groups --all-extras

[doc('Format code')]
[group('dev')]
fmt:
    uv run ruff check --select I --fix
    uv run ruff format

[doc('Remove build artifacts')]
[group('dev')]
clean:
    rm -rf dist .pytest_cache .ruff_cache

[doc('Run pytest tests')]
[group('test')]
test:
    uv run pytest -v

[doc('Run bats integration tests')]
[group('test')]
bats:
    bats -T tests/bats

[doc('Run all tests')]
[group('test')]
test-all: test bats

[doc('Run linters')]
[group('test')]
lint:
    uv run ruff check
    uv run ty check

[doc('Benchmark startup time')]
[group('bench')]
bench-startup:
    hyperfine --warmup 3 --min-runs 10 ".venv/bin/jinja2 --version"

[doc('Build docker image')]
[group('docker')]
docker:
    docker build --rm -t jinja2-cli .

[doc('Print docker bake configuration')]
[group('docker')]
bake:
    VERSION=$(uv version --short) LATEST_TAG=dev \
        docker buildx bake --print

[doc('Build distribution packages')]
[group('release')]
build: clean
    uv build

[doc('Publish to PyPI')]
[group('release')]
publish: build
    uv publish

[doc('Bump version, commit, tag, and push')]
[group('release')]
bump kind:
    git diff --quiet --exit-code
    uv version --bump {{ kind }}
    git commit -am "bump $(uv version --short)"
    git tag -a "v$(uv version --short)" -m "v$(uv version --short)"
    git push
    git push origin "v$(uv version --short)"
