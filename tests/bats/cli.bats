#!/usr/bin/env bats

fixtures_dir="${BATS_TEST_DIRNAME}/../fixtures"
helpers_dir="${BATS_TEST_DIRNAME}/../helpers"
formats_dir="${fixtures_dir}/formats"
unicode_dir="${fixtures_dir}/unicode"
extensions_dir="${fixtures_dir}/extensions"
env_opts_dir="${fixtures_dir}/env_opts"
include_paths_dir="${fixtures_dir}/include_paths"
environ_dir="${fixtures_dir}/environ"

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

    [ "$status" -eq 0 ]
    [ "$output" = "Hello Matt" ]
}

@test "renders ini file" {
    run uv run jinja2 "$formats_dir/template_section.j2" "$formats_dir/data.ini" --format ini

    [ "$status" -eq 0 ]
    [ "$output" = "bar" ]
}

@test "renders querystring from stdin" {
    run bash -c "cat '$formats_dir/data.querystring' | uv run jinja2 '$formats_dir/template_querystring.j2' - --format querystring"

    [ "$status" -eq 0 ]
    [ "$output" = "bar spam" ]
}

@test "renders from stdin" {
    run bash -c "cat '$formats_dir/data.json' | uv run jinja2 '$formats_dir/template_name.j2' - --format json"

    [ "$status" -eq 0 ]
    [ "$output" = "Hello Matt" ]
}

@test "renders env file" {
    run uv run jinja2 "$formats_dir/template_env.j2" "$formats_dir/data.env" --format env

    [ "$status" -eq 0 ]
    [ "$output" = "bar baz" ]
}

@test "renders yaml file" {
    require_module yaml
    run uv run jinja2 "$formats_dir/template_name.j2" "$formats_dir/data.yaml" --format yaml

    [ "$status" -eq 0 ]
    [ "$output" = "Hello Matt" ]
}

@test "renders toml file" {
    require_toml
    run uv run jinja2 "$formats_dir/template_name.j2" "$formats_dir/data.toml" --format toml

    [ "$status" -eq 0 ]
    [ "$output" = "Hello Matt" ]
}

@test "renders xml file" {
    require_module xmltodict
    run uv run jinja2 "$formats_dir/template_root_name.j2" "$formats_dir/data.xml" --format xml

    [ "$status" -eq 0 ]
    [ "$output" = "Matt" ]
}

@test "renders hjson file" {
    require_module hjson
    run uv run jinja2 "$formats_dir/template_name.j2" "$formats_dir/data.hjson" --format hjson

    [ "$status" -eq 0 ]
    [ "$output" = "Hello Matt" ]
}

@test "renders json5 file" {
    require_module json5
    run uv run jinja2 "$formats_dir/template_name.j2" "$formats_dir/data.json5" --format json5

    [ "$status" -eq 0 ]
    [ "$output" = "Hello Matt" ]
}

@test "trim blocks" {
    run uv run jinja2 "$env_opts_dir/trim_blocks.j2" "$env_opts_dir/empty.json" --format json --trim-blocks

    [ "$status" -eq 0 ]
    [ "$output" = "foo" ]
}

@test "lstrip blocks" {
    run uv run jinja2 "$env_opts_dir/lstrip_blocks.j2" "$env_opts_dir/empty.json" --format json --lstrip-blocks

    [ "$status" -eq 0 ]
    [ "$output" = "foo" ]
}

@test "custom variable delimiters" {
    run uv run jinja2 "$env_opts_dir/variable_delims.j2" "$formats_dir/data.json" --format json --variable-start "<<" --variable-end ">>"

    [ "$status" -eq 0 ]
    [ "$output" = "Hello Matt" ]
}

@test "line statement prefix" {
    run uv run jinja2 "$env_opts_dir/line_statement.j2" "$env_opts_dir/empty.json" --format json --line-statement-prefix "%"

    [ "$status" -eq 0 ]
    [ "$output" = "Hello" ]
}

@test "loads local extension from cwd" {
    run bash -c "cd '$extensions_dir' && uv run jinja2 template.j2 data.json --format json -e myext:ShoutExtension"

    [ "$status" -eq 0 ]
    [ "$output" = "MATT" ]
}

@test "unicode from json file" {
    run uv run jinja2 "$unicode_dir/template_title.j2" "$unicode_dir/data_title.json" --format json

    [ "$status" -eq 0 ]
    [ "$output" = "café ☕️ — jalapeño 🌶️" ]
}

@test "unicode in template" {
    run uv run jinja2 "$unicode_dir/template_greeting.j2" "$unicode_dir/data_name.json" --format json

    [ "$status" -eq 0 ]
    [ "$output" = "Hello 🌍 — Zoë" ]
}

@test "unicode via stdin" {
    run bash -c "cat '$unicode_dir/data_stdin.json' | uv run jinja2 '$unicode_dir/template_title.j2' - --format json"

    [ "$status" -eq 0 ]
    [ "$output" = "naïve 🧪 — résumé" ]
}

@test "include path allows importing from other directory" {
    run uv run jinja2 "$include_paths_dir/pages/home.j2" "$include_paths_dir/data.json" --format json -I "$include_paths_dir"

    [ "$status" -eq 0 ]
    [ "$output" = "<button>Click me</button>" ]
}

@test "environ returns None for missing var without --strict" {
    unset JINJA2_CLI_TEST_VAR
    run uv run jinja2 "$environ_dir/template.j2" "$environ_dir/empty.json" --format json

    [ "$status" -eq 0 ]
    [ "$output" = "None" ]
}

@test "environ fails for missing var with --strict" {
    unset JINJA2_CLI_TEST_VAR
    run uv run jinja2 "$environ_dir/template.j2" "$environ_dir/empty.json" --format json --strict

    [ "$status" -eq 1 ]
    [[ "$output" == *"environment variable 'JINJA2_CLI_TEST_VAR' is not defined"* ]]
}

@test "environ works for existing var with --strict" {
    export JINJA2_CLI_TEST_VAR=hello
    run uv run jinja2 "$environ_dir/template.j2" "$environ_dir/empty.json" --format json --strict

    [ "$status" -eq 0 ]
    [ "$output" = "hello" ]
}

@test "output file preserved on render failure" {
    tmp_out="$(mktemp)"
    echo "original content" >"$tmp_out"

    # Template with undefined var should fail with --strict
    run uv run jinja2 "$environ_dir/template.j2" "$environ_dir/empty.json" --format json --strict -o "$tmp_out"

    [ "$status" -eq 1 ]
    [ "$(cat "$tmp_out")" = "original content" ]
    rm -f "$tmp_out"
}

@test "same file for input and output works" {
    tmp_file="$(mktemp)"
    echo "hello {{ name }}" >"$tmp_file"

    run uv run jinja2 -D name=world -o "$tmp_file" "$tmp_file"

    [ "$status" -eq 0 ]
    [ "$(cat "$tmp_file")" = "hello world" ]
    rm -f "$tmp_file"
}
