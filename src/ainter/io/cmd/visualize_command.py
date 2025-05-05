from argparse import ArgumentParser, Namespace

from ainter.io.cmd.command import CMDCommand
from ainter.visualization.server_nasch import server
import osmnx as ox


class VisualizeCommand(CMDCommand):

    def configure_parser(self, subparser) -> ArgumentParser:
        parser: ArgumentParser = subparser.add_parser(name='visualize',
                                                      help='Runs the MESA server for NaSch model') 
        return parser

    def __call__(self, args: Namespace) -> None:
            server.launch()
    
    def __init__(self):
         ox.settings.use_cache = False
