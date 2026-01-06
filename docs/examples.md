# Examples

## Render config in a container entrypoint
A common pattern is to render config files at container startup from env vars
and a template.

`Dockerfile`:
```
COPY nginx.conf.j2 /etc/nginx/nginx.conf.j2
COPY docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
```

`docker-entrypoint.sh`:
```
#!/usr/bin/env sh
set -e

jinja2 /etc/nginx/nginx.conf.j2 - --format env <<EOF >/etc/nginx/nginx.conf
SERVER_NAME=$SERVER_NAME
UPSTREAM=$UPSTREAM
EOF

exec nginx -g "daemon off;"
```

## Render a file from JSON
```
$ jinja2 template.j2 data.json --format json
```

## Render a file from YAML
```
$ jinja2 template.j2 data.yaml --format yaml
```

## Render from stdin
```
$ cat data.json | jinja2 template.j2 - --format json
```

## Inline variables
```
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
```
$ jinja2 template.j2 - --format env <<'EOF'
PATH=$PATH
USER=$USER
USERNAME=$USERNAME
EOF
```

## Extensions
```
$ jinja2 template.j2 data.json -e do -e loopcontrols
$ jinja2 template.j2 data.json -e myext:MyExtension
```

## In the wild
If you have public examples (blog posts, repos, or Docker images) that use
`jinja2-cli`, add a link here.
