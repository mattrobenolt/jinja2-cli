# Formats

Use `--format` to specify the input data format. The default is `auto`.

| Format | Flag | Extra | Notes |
| --- | --- | --- | --- |
| JSON | `json` | none | Built in |
| INI | `ini` | none | Built in |
| YAML | `yaml` / `yml` | `yaml` | `pyyaml` required |
| TOML | `toml` | `toml` | `tomli` required on Python < 3.11 |
| XML | `xml` | `xml` | `xmltodict` required |
| ENV | `env` | none | `KEY=value` lines |
| Querystring | `querystring` | none | URL querystring format |
| HJSON | `hjson` | `hjson` | `hjson` required |
| JSON5 | `json5` | `json5` | `json5` required |

Install an extra with uv or pip, for example:
```
$ uv tool install jinja2-cli[yaml]
# or
$ pip install jinja2-cli[yaml]
```
