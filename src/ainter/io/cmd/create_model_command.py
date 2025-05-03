import dataclasses
import json
from argparse import ArgumentParser, FileType, Namespace
from pathlib import Path

import networkx as nx
import osmnx as ox

from ainter.io.cmd.command import CMDCommand
from ainter.configs.env_creation import EnvConfig
from ainter.models.nagel_schreckenberg.environment import Environment
from ainter.models.nagel_schreckenberg.model import Model
from ainter.models.vehicles.vehicle import Vehicle


class CreateModelCommand(CMDCommand):

    def __init__(self) -> None:
        ox.settings.use_cache = False
        ox.settings.log_console = False

    def configure_parser(self, subparser) -> ArgumentParser:
        parser: ArgumentParser = subparser.add_parser(name='create_model',
                                                      help='Creates model from specification and saves it to given output file')

        parser.add_argument('-i', '--input',
                            help='Configuration in .JSON format that describes env settings',
                            type=FileType(mode='r', encoding='UTF-8'),
                            nargs='?',
                            dest='input',
                            required=True)
        parser.add_argument('-o', '--output',
                            help='Save location for created environment file',
                            type=Path,
                            nargs='?',
                            dest='output',
                            required=True)

        return parser

    def __call__(self, args: Namespace) -> None:
        config = self.process_input(args.input)
        model = Model.from_config(config)
        print('AAA')

    def process_input(self, input_file) -> EnvConfig:
        data = json.load(input_file, object_hook=EnvConfig.from_json)
        return data