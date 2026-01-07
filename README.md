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

## Used by
- [Dangerzone](https://github.com/freedomofpress/dangerzone) by Freedom of the Press Foundation
- [Elastic](https://github.com/elastic/logstash-docker) Docker images (Logstash, Kibana, Beats)
- [ScyllaDB](https://github.com/scylladb/scylla-machine-image) CloudFormation templates
- [800+ more](https://github.com/mattrobenolt/jinja2-cli/network/dependents) on GitHub

## Available in
[![PyPI](https://img.shields.io/pypi/v/jinja2-cli)](https://pypi.org/project/jinja2-cli/)
[![Homebrew](https://img.shields.io/homebrew/v/jinja2-cli)](https://formulae.brew.sh/formula/jinja2-cli)
[![nixpkgs](https://img.shields.io/badge/nixpkgs-jinja2--cli-blue)](https://search.nixos.org/packages?query=jinja2-cli)
[![AUR](https://img.shields.io/aur/version/jinja2-cli)](https://aur.archlinux.org/packages/jinja2-cli)
[![Alpine](https://img.shields.io/badge/Alpine-jinja2--cli-0D597F?logo=alpinelinux&logoColor=fff)](https://pkgs.alpinelinux.org/package/edge/community/x86_64/jinja2-cli)

## Learn more
- [Jinja2 as a Command Line Application](https://thejeshgn.com/2021/12/07/jinja2-command-line-application/)
- [Combining jinja2-cli with jq and environment variables](https://www.zufallsheld.de/2025/06/30/templating-jinja-cli)
