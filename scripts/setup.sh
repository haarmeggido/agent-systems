#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

log_installation_location () {
  	local python_location
  	python_location="$(which python)"

  	printf "Will begin setup of the package using python at: \"%s\"\n" "$python_location"
}

log_installation_location

pip install -e .

exit 0