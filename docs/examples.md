# Examples

## Render config in a container entrypoint
A common pattern is to render config files at container startup from env vars
and a template.

`Dockerfile`:
```Dockerfile
COPY nginx.conf.j2 /etc/nginx/nginx.conf.j2
COPY docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
```

`docker-entrypoint.sh`:
```sh
#!/usr/bin/env sh
set -e

jinja2 /etc/nginx/nginx.conf.j2 - --format env <<EOF >/etc/nginx/nginx.conf
SERVER_NAME=$SERVER_NAME
UPSTREAM=$UPSTREAM
EOF

exec nginx -g "daemon off;"
```

## Render a file from JSON
```sh
$ jinja2 template.j2 data.json --format json
```

## Render a file from YAML
```sh
$ jinja2 template.j2 data.yaml --format yaml
```

## Render from stdin
```sh
$ cat data.json | jinja2 template.j2 - --format json
```

## Inline variables
```sh
$ jinja2 template.j2 data.json --format json -D foo=bar -D answer=42
```

## Environment variables
Template:
```
PATH is {{ environ('PATH') }}
USER is {{ environ('USER') }}
USERNAME is {{ environ('USERNAME') }}
```

Run:
```sh
$ jinja2 template.j2 - --format env <<'EOF'
PATH=$PATH
USER=$USER
USERNAME=$USERNAME
EOF
```

## Extensions
```sh
$ jinja2 template.j2 data.json -e do -e loopcontrols
$ jinja2 template.j2 data.json -e myext:MyExtension
```

## Include paths
Use `-I` to add directories to the template search path. This is useful when
templates need to include or import from a shared directory:

```
project/
├── templates/
│   ├── macros/
│   │   └── buttons.j2
│   └── pages/
│       └── home.j2
└── data.json
```

`home.j2`:
```jinja
{% from "macros/buttons.j2" import button %}
{{ button("Click me") }}
```

```
$ jinja2 templates/pages/home.j2 data.json -I templates/
```

## In the wild

### Dangerzone
[Freedom of the Press Foundation](https://freedom.press/) uses jinja2-cli to
generate Dockerfiles for [Dangerzone](https://github.com/freedomofpress/dangerzone),
a tool for converting potentially dangerous PDFs into safe ones.

See: [Makefile](https://github.com/freedomofpress/dangerzone/blob/main/Makefile)
```make
poetry run jinja2 Dockerfile.in Dockerfile.env > Dockerfile
```

### Elastic Docker Images
Elastic uses jinja2-cli to generate Dockerfiles and docker-compose configs for
their official [Beats](https://github.com/elastic/beats-docker),
[Logstash](https://github.com/elastic/logstash-docker), and
[Kibana](https://github.com/elastic/kibana-docker) Docker images.

See: [beats-docker Makefile](https://github.com/elastic/beats-docker/blob/master/Makefile)
```make
jinja2 -D beat=$@ -D elastic_version=$(ELASTIC_VERSION) \
  templates/Dockerfile.j2 > build/$@/Dockerfile-full
```

### ScyllaDB
[ScyllaDB](https://www.scylladb.com/) uses jinja2-cli in their
[machine image tooling](https://github.com/scylladb/scylla-machine-image) for
generating cloud deployment configurations.

---

Have a public example? Add a link here.
