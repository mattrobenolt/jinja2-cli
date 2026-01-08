#!/usr/bin/env bats

fixtures_dir="${BATS_TEST_DIRNAME}/../fixtures"
helpers_dir="${BATS_TEST_DIRNAME}/../helpers"
formats_dir="${fixtures_dir}/formats"
unicode_dir="${fixtures_dir}/unicode"
extensions_dir="${fixtures_dir}/extensions"
env_opts_dir="${fixtures_dir}/env_opts"
include_paths_dir="${fixtures_dir}/include_paths"
environ_dir="${fixtures_dir}/environ"
filters_dir="${fixtures_dir}/filters"
dot_notation_dir="${fixtures_dir}/dot_notation"

setup() {
    bats_load_library bats-support
    bats_load_library bats-assert
    bats_load_library bats-file

    bats_require_minimum_version 1.12.0

    TEST_TEMP_DIR="$(temp_make)"
}

teardown() {
    temp_del "$TEST_TEMP_DIR"
}

require_module() {
    if ! uv run python "$helpers_dir/has_module.py" "$1"; then
        skip "$1 not installed"
    fi
}

require_toml() {
    if ! uv run python "$helpers_dir/has_toml.py"; then
        skip "toml not available"
    fi
}

@test "renders json file" {
    run uv run jinja2 "$formats_dir/template_name.j2" "$formats_dir/data.json" --format json

    assert_success
    assert_output "Hello Matt"
}

@test "renders ini file" {
    run uv run jinja2 "$formats_dir/template_section.j2" "$formats_dir/data.ini" --format ini

    assert_success
    assert_output "bar"
}

@test "renders querystring from stdin" {
    run bash -c "cat '$formats_dir/data.querystring' | uv run jinja2 '$formats_dir/template_querystring.j2' - --format querystring"

    assert_success
    assert_output "bar spam"
}

@test "renders from stdin" {
    run bash -c "cat '$formats_dir/data.json' | uv run jinja2 '$formats_dir/template_name.j2' - --format json"

    assert_success
    assert_output "Hello Matt"
}

@test "renders env file" {
    run uv run jinja2 "$formats_dir/template_env.j2" "$formats_dir/data.env" --format env

    assert_success
    assert_output "bar baz"
}

@test "renders yaml file" {
    require_module yaml
    run uv run jinja2 "$formats_dir/template_name.j2" "$formats_dir/data.yaml" --format yaml

    assert_success
    assert_output "Hello Matt"
}

@test "renders toml file" {
    require_toml
    run uv run jinja2 "$formats_dir/template_name.j2" "$formats_dir/data.toml" --format toml

    assert_success
    assert_output "Hello Matt"
}

@test "renders xml file" {
    require_module xmltodict
    run uv run jinja2 "$formats_dir/template_root_name.j2" "$formats_dir/data.xml" --format xml

    assert_success
    assert_output "Matt"
}

@test "renders hjson file" {
    require_module hjson
    run uv run jinja2 "$formats_dir/template_name.j2" "$formats_dir/data.hjson" --format hjson

    assert_success
    assert_output "Hello Matt"
}

@test "renders json5 file" {
    require_module json5
    run uv run jinja2 "$formats_dir/template_name.j2" "$formats_dir/data.json5" --format json5

    assert_success
    assert_output "Hello Matt"
}

@test "trim blocks" {
    run uv run jinja2 "$env_opts_dir/trim_blocks.j2" "$env_opts_dir/empty.json" --format json --trim-blocks

    assert_success
    assert_output "foo"
}

@test "lstrip blocks" {
    run uv run jinja2 "$env_opts_dir/lstrip_blocks.j2" "$env_opts_dir/empty.json" --format json --lstrip-blocks

    assert_success
    assert_output "foo"
}

@test "custom variable delimiters" {
    run uv run jinja2 "$env_opts_dir/variable_delims.j2" "$formats_dir/data.json" --format json --variable-start "<<" --variable-end ">>"

    assert_success
    assert_output "Hello Matt"
}

@test "line statement prefix" {
    run uv run jinja2 "$env_opts_dir/line_statement.j2" "$env_opts_dir/empty.json" --format json --line-statement-prefix "%"

    assert_success
    assert_output "Hello"
}

@test "loads local extension from cwd" {
    run bash -c "cd '$extensions_dir' && uv run jinja2 template.j2 data.json --format json -e myext:ShoutExtension"

    assert_success
    assert_output "MATT"
}

@test "unicode from json file" {
    run uv run jinja2 "$unicode_dir/template_title.j2" "$unicode_dir/data_title.json" --format json

    assert_success
    assert_output "café ☕️ — jalapeño 🌶️"
}

@test "unicode in template" {
    run uv run jinja2 "$unicode_dir/template_greeting.j2" "$unicode_dir/data_name.json" --format json

    assert_success
    assert_output "Hello 🌍 — Zoë"
}

@test "unicode via stdin" {
    run bash -c "cat '$unicode_dir/data_stdin.json' | uv run jinja2 '$unicode_dir/template_title.j2' - --format json"

    assert_success
    assert_output "naïve 🧪 — résumé"
}

@test "include path allows importing from other directory" {
    run uv run jinja2 "$include_paths_dir/pages/home.j2" "$include_paths_dir/data.json" --format json -I "$include_paths_dir"

    assert_success
    assert_output "<button>Click me</button>"
}

@test "environ returns None for missing var without --strict" {
    unset JINJA2_CLI_TEST_VAR
    run uv run jinja2 "$environ_dir/template.j2" "$environ_dir/empty.json" --format json

    assert_success
    assert_output "None"
}

@test "environ fails for missing var with --strict" {
    unset JINJA2_CLI_TEST_VAR
    run uv run jinja2 "$environ_dir/template.j2" "$environ_dir/empty.json" --format json --strict

    assert_failure
    assert_output --partial "environment variable 'JINJA2_CLI_TEST_VAR' is not defined"
}

@test "environ works for existing var with --strict" {
    export JINJA2_CLI_TEST_VAR=hello
    run uv run jinja2 "$environ_dir/template.j2" "$environ_dir/empty.json" --format json --strict

    assert_success
    assert_output "hello"
}

@test "output file preserved on render failure" {
    tmp_out="$(mktemp)"
    echo "original content" >"$tmp_out"

    # Template with undefined var should fail with --strict
    run uv run jinja2 "$environ_dir/template.j2" "$environ_dir/empty.json" --format json --strict -o "$tmp_out"

    assert_failure
    [ "$(cat "$tmp_out")" = "original content" ]
    rm -f "$tmp_out"
}

@test "same file for input and output works" {
    tmp_file="$(mktemp)"
    echo "hello {{ name }}" >"$tmp_file"

    run uv run jinja2 -D name=world -o "$tmp_file" "$tmp_file"

    assert_success
    [ "$(cat "$tmp_file")" = "hello world" ]
    rm -f "$tmp_file"
}

@test "stream mode renders template from stdin" {
    run bash -c "echo '{{ 1 + 1 }}' | uv run jinja2 -S"

    assert_success
    assert_output "2"
}

@test "stream mode with -D variables" {
    run bash -c "echo 'Hello {{ name }}!' | uv run jinja2 -S -D name=world"

    assert_success
    assert_output "Hello world!"
}

@test "stream mode with environ" {
    run bash -c "export TEST_VAR=foobar && echo '{{ environ(\"TEST_VAR\") }}' | uv run jinja2 -S"

    assert_success
    assert_output "foobar"
}

@test "stream mode with output file" {
    tmp_out="$(mktemp)"

    run bash -c "echo 'hello world' | uv run jinja2 -S -o '$tmp_out'"

    assert_success
    [ "$(cat "$tmp_out")" = "hello world" ]
    rm -f "$tmp_out"
}

@test "loads single custom filter function" {
    run bash -c "cd '$filters_dir' && uv run jinja2 template_single.j2 data.json --format json --filter custom.reverse"

    assert_success
    assert_output "olleh"
}

@test "loads multiple custom filter functions" {
    run bash -c "cd '$filters_dir' && uv run jinja2 template.j2 data.json --format json --filter custom.reverse --filter custom.multiply --filter custom.shout"

    assert_success
    assert_output "olleh
15
HI!"
}

@test "loads filters from module dict" {
    run bash -c "cd '$filters_dir' && uv run jinja2 template.j2 data.json --format json --filter custom.filters"

    assert_success
    assert_output "olleh
15
HI!"
}

@test "loads filters from module with filters attribute" {
    run bash -c "cd '$filters_dir' && uv run jinja2 template.j2 data.json --format json --filter custom"

    assert_success
    assert_output "olleh
15
HI!"
}

@test "auto-discovers filters from module" {
    run bash -c "cd '$filters_dir' && uv run jinja2 template_autodiscover.j2 data_autodiscover.json --format json --filter autodiscover"

    assert_success
    assert_output "HELLO
hello
10"
}

@test "loads ansible filters via helper function" {
    require_module ansible
    run bash -c "cd '$filters_dir' && uv run jinja2 template_ansible.j2 data_ansible.json --format json --filter ansible_helper.load_core_filters"

    assert_success
    assert_output --partial "'a': 1"
    assert_output --partial "'b': 2"
}

@test "loads ansible filters directly from FilterModule class" {
    require_module ansible
    run bash -c "cd '$filters_dir' && uv run jinja2 template_ansible.j2 data_ansible.json --format json --filter ansible.plugins.filter.core.FilterModule"

    assert_success
    assert_output --partial "'a': 1"
    assert_output --partial "'b': 2"
}

@test "loads ansible filters using simplified module syntax" {
    require_module ansible
    run bash -c "cd '$filters_dir' && uv run jinja2 template_ansible.j2 data_ansible.json --format json -F ansible.plugins.filter.core"

    assert_success
    assert_output --partial "'a': 1"
    assert_output --partial "'b': 2"
}

@test "supports dot notation in -D parameters" {
    run uv run jinja2 "$dot_notation_dir/template.j2" "$dot_notation_dir/data.json" --format json -D server.port=8080 -D auth.username=admin -D simple=value

    assert_success
    assert_output --partial "Server: localhost:8080"
    assert_output --partial "Auth: admin:default"
    assert_output --partial "Simple: value"
}

@test "env format supports multiline values" {
    cat >/tmp/test_multiline.env <<'EOF'
FOO="first line\nsecond line"
BAR=simple
BAZ="with\ttab"
EOF

    cat >/tmp/test_multiline.j2 <<'EOF'
FOO: {{ FOO }}
BAR: {{ BAR }}
BAZ: {{ BAZ }}
EOF

    run uv run jinja2 /tmp/test_multiline.j2 /tmp/test_multiline.env --format env

    assert_success
    assert_output --partial "FOO: first line"
    assert_output --partial "second line"
    assert_output --partial "BAR: simple"
    assert_output --partial "with	tab"

    rm -f /tmp/test_multiline.env /tmp/test_multiline.j2
}

@test "supports multiple data files with deep merge" {
    cat >"$TEST_TEMP_DIR/base.json" <<'EOF'
{
  "name": "Base",
  "server": {
    "host": "localhost",
    "port": 3000
  },
  "debug": false
}
EOF

    cat >"$TEST_TEMP_DIR/override.yaml" <<'EOF'
server:
  port: 8080
debug: true
EOF

    cat >"$TEST_TEMP_DIR/test_multi.j2" <<'EOF'
Name: {{ name }}
Server: {{ server.host }}:{{ server.port }}
Debug: {{ debug }}
EOF

    require_module yaml

    run uv run jinja2 "$TEST_TEMP_DIR/test_multi.j2" "$TEST_TEMP_DIR/base.json" "$TEST_TEMP_DIR/override.yaml"

    assert_success
    assert_output --partial "Name: Base"
    assert_output --partial "Server: localhost:8080"
    assert_output --partial "Debug: True"
}

@test "errors when mixing stdin with file arguments" {
    cat >"$TEST_TEMP_DIR/base.json" <<'EOF'
{"name": "test"}
EOF

    cat >"$TEST_TEMP_DIR/test.j2" <<'EOF'
{{ name }}
EOF

    run uv run jinja2 "$TEST_TEMP_DIR/test.j2" - "$TEST_TEMP_DIR/base.json"

    assert_failure
    assert_output --partial "Cannot mix stdin (-) with file arguments"
}

@test "stream mode supports data files" {
    cat >"$TEST_TEMP_DIR/stream_data.json" <<'EOF'
{"name": "World"}
EOF

    run bash -c "echo 'Hello {{ name }}!' | uv run jinja2 -S '$TEST_TEMP_DIR/stream_data.json'"

    assert_success
    assert_output --partial "Hello World!"
}

@test "stream mode supports multiple data files" {
    cat >"$TEST_TEMP_DIR/stream_base.json" <<'EOF'
{"name": "Base", "greeting": "Hello"}
EOF

    cat >"$TEST_TEMP_DIR/stream_override.yaml" <<'EOF'
name: World
EOF

    require_module yaml

    run bash -c "echo '{{ greeting }} {{ name }}!' | uv run jinja2 -S '$TEST_TEMP_DIR/stream_base.json' '$TEST_TEMP_DIR/stream_override.yaml'"

    assert_success
    assert_output --partial "Hello World!"
}
