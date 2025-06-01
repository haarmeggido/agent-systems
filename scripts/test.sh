#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

coverage run --parallel-mode --source ./src/ainter -m pytest -n auto .
coverage combine
coverage report

exit 0