variable "VERSION" {
  default = ""
}

variable "LATEST_TAG" {
  default = "latest"
}

variable "REGISTRY" {
  default = "ghcr.io/mattrobenolt/jinja2"
}

function "major" {
  params = [version]
  result = split(".", version)[0]
}

function "minor" {
  params = [version]
  result = "${split(".", version)[0]}.${split(".", version)[1]}"
}

function "tags" {
  params = [registry, version, latest_tag]
  result = latest_tag != "latest" ? [
    "${registry}:${latest_tag}"
  ] : notequal("", version) ? [
    "${registry}:${version}",
    "${registry}:${minor(version)}",
    "${registry}:${major(version)}",
    "${registry}:${latest_tag}"
  ] : ["${registry}:${latest_tag}"]
}

group "default" {
  targets = ["jinja2-cli"]
}

target "jinja2-cli" {
  context = "."
  dockerfile = "Dockerfile"
  platforms = ["linux/amd64", "linux/arm64"]
  tags = tags(REGISTRY, VERSION, LATEST_TAG)
}
