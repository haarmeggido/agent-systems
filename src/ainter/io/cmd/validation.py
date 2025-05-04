import argparse


class UnsignedInteger(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None) -> None:
        values_int = int(values, 10)
        if values_int < 1:
            raise ValueError("Not an unsigned integer")

        setattr(namespace, self.dest, values_int)
