#!/bin/sh
# Example of passing classic shell list to jijna2
# Appropriate for classic shell scripts that use space-delimited list variables
# Uses yaml to avoid needing to strip trailing comma

list2yml() {
  local name
  name=$1
  shift
  echo "$name:"
  for item
  do
     echo "- $item"
  done
}

val2yml() {
  echo "$1: $2"
}

ITEMS="apple banana cherry"

(list2yml items $ITEMS; val2yml foo true) | jinja2 sample.jinja2
