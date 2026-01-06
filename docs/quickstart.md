# Quickstart

## Install
```
$ uv tool install jinja2-cli
# or
$ pip install jinja2-cli
```

## Render from a data file
```
$ jinja2 template.j2 data.json --format json
```

## Render from stdin
```
$ cat data.json | jinja2 template.j2 - --format json
```

## Inline variables
```
$ jinja2 template.j2 data.json --format json -D foo=bar -D answer=42
```

## Auto format
- If a data file is provided, `--format auto` (default) uses the file extension.
- If stdin is used, it defaults to YAML when available, otherwise JSON.
