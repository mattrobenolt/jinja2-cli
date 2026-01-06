#!/usr/bin/env bats

fixtures_dir="${BATS_TEST_DIRNAME}/../fixtures"
helpers_dir="${BATS_TEST_DIRNAME}/../helpers"
formats_dir="${fixtures_dir}/formats"
unicode_dir="${fixtures_dir}/unicode"
extensions_dir="${fixtures_dir}/extensions"

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
