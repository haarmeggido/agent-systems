#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

# TODO: Change the location os the pytest command sees the pytest.ini and pyproject.toml
pytest --cov=ainter

exit 0