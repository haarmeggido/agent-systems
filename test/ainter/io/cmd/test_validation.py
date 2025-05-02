import argparse

from ainter.io.cmd.validation import UnsignedInteger

import pytest


def test_valid_unsigned_integer():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", action=UnsignedInteger)

    args = parser.parse_args(["--count", "5"])
    assert args.count == 5

@pytest.mark.parametrize("invalid_input", ["0", "-1", "abc"])
def test_invalid_unsigned_integer(invalid_input):
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", action=UnsignedInteger)

    with pytest.raises(ValueError):
        parser.parse_args(["--count", invalid_input])
