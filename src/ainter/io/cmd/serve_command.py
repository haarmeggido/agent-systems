from argparse import ArgumentParser, Namespace

from ainter.io.cmd.command import CMDCommand
from ainter.visualization.server import server


class ServeCommand(CMDCommand):

    def configure_parser(self, subparser) -> ArgumentParser:
        parser: ArgumentParser = subparser.add_parser(name='serve',
                                                      help='Runs the MESA server')
        return parser

    def __call__(self, args: Namespace) -> None:
            server.launch()
