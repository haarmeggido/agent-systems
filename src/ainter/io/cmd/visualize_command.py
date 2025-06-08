import os
from argparse import ArgumentParser, Namespace, FileType

import osmnx as ox
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Mount

from ainter.configs.env_creation import get_env_config_from_json
from ainter.io.cmd.command import CMDCommand
from ainter.visualization.solara import set_environment_config


class VisualizeCommand(CMDCommand):

    def __init__(self):
        ox.settings.use_cache = False
        ox.settings.log_console = False

        # Make sure that the os.environ["SOLARA_APP"] = ... is called before import solara.server.starlette
        if "SOLARA_APP" not in os.environ:
            os.environ["SOLARA_APP"] = "ainter.visualization.solara"

    def __call__(self, args: Namespace) -> None:
        env_config = get_env_config_from_json(args.input)
        # Make sure that the set_environment_config(env_config) is called before import solara.server.starlette
        set_environment_config(env_config)

        self.configure_run_server(args)

    def configure_run_server(self, args: Namespace) -> None:
        import solara.server.starlette
        routes = [
            Mount('/', routes=solara.server.starlette.routes),
        ]

        app = Starlette(routes=routes)
        uvicorn.run(app, host=args.host, port=args.port, lifespan="on")

    def configure_parser(self, subparser) -> ArgumentParser:
        parser: ArgumentParser = subparser.add_parser(name='visualize',
                                                      help='Starts the solara visualization server')

        parser.add_argument('-i', '--input',
                            help='Configuration in .JSON format that describes env settings',
                            type=FileType(mode='r', encoding='UTF-8'),
                            nargs='?',
                            dest='input',
                            required=True)
        parser.add_argument('--port',
                            help='Port, on which the visualization server will listen',
                            type=int,
                            default=8765,
                            dest='port')
        parser.add_argument('--host',
                            help='Host, on which the visualization server will listen',
                            type=str,
                            default="127.0.0.1",
                            dest='host')
        return parser
