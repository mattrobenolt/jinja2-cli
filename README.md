# $ jinja2

A CLI for [Jinja2](https://jinja.palletsprojects.com/).

```
$ jinja2 template.j2 data.json
$ cat data.json | jinja2 template.j2
$ curl -s http://api.example.com | jinja2 template.j2
```

## Install
```
$ uv tool install jinja2-cli
$ pip install jinja2-cli
```

## Formats
Built-in: JSON, INI, ENV, querystring, TOML (Python 3.11+)

Optional formats via extras:
```
$ pip install jinja2-cli[yaml]
$ pip install jinja2-cli[xml]
$ pip install jinja2-cli[hjson]
$ pip install jinja2-cli[json5]
```

## Features
- Read data from files or stdin
- Define variables inline with `-D key=value`
- Custom Jinja2 extensions
- Full control over Jinja2 environment options

Run `jinja2 --help` for all options, or see [docs/](docs/) for full documentation.
