# Development

## Setup with Nix (recommended)
If you have [Nix](https://nixos.org/) and [direnv](https://direnv.net/) installed:
```
git clone https://github.com/mattrobenolt/jinja2-cli.git
cd jinja2-cli
direnv allow
```

This provides all dependencies: uv, just, bats, hyperfine, and shellcheck.

## Setup without Nix
Prerequisites:
- Python 3.8+
- [uv](https://docs.astral.sh/uv/)
- [just](https://github.com/casey/just) (optional, for task running)
- [bats](https://github.com/bats-core/bats-core) (for CLI tests)

```
git clone https://github.com/mattrobenolt/jinja2-cli.git
cd jinja2-cli
uv sync --all-groups --all-extras
```

## Running tests
```
just test-all    # Run pytest and bats
just test        # Run pytest only
just bats        # Run bats only
```

Or without just:
```
uv run pytest -v
bats tests/bats
```

## Linting
```
just lint
```

Or:
```
uv run ruff check
```

## Formatting
```
just fmt
```

## Building
```
just build
```

This creates a wheel in `dist/`.
