FROM cgr.dev/chainguard/wolfi-base:latest AS build
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /bin

USER nonroot

WORKDIR /app

COPY . /app
RUN uv sync \
    --verbose --no-dev --all-extras --locked \
    --no-cache-dir --no-editable --compile-bytecode \
    && rm -rf /home/nonroot/.local/share/uv/python/cpython-*-gnu/share \
    && rm -rf /home/nonroot/.local/share/uv/python/cpython-*-gnu/lib/tcl8* \
    && rm -rf /home/nonroot/.local/share/uv/python/cpython-*-gnu/lib/libtcl8* \
    && rm -rf /home/nonroot/.local/share/uv/python/cpython-*-gnu/lib/tk8* \
    && rm -rf /home/nonroot/.local/share/uv/python/cpython-*-gnu/lib/libtk8*

RUN /app/.venv/bin/jinja2 --version

FROM cgr.dev/chainguard/wolfi-base:latest

LABEL org.opencontainers.image.source="https://github.com/mattrobenolt/jinja2-cli"
LABEL org.opencontainers.image.description="The CLI interface to Jinja2"
LABEL org.opencontainers.image.licenses="BSD-2-Clause"

COPY --from=build --chown=nonroot:nonroot \
    /home/nonroot/.local/share/uv/ /home/nonroot/.local/share/uv/
COPY --from=build --chown=nonroot:nonroot \
    /app/.venv/ /app/.venv/

USER nonroot

ENTRYPOINT ["/app/.venv/bin/jinja2"]
CMD ["--help"]
