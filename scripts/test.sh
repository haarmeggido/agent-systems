#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

pytest -n auto

exit 0