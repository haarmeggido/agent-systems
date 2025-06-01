#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

pytest -n 0 .

exit 0