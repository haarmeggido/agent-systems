from argparse import ArgumentParser

from ainter.io.cmd.create_model_command import CreateModelCommand
from ainter.io.cmd.serve_command import ServeCommand
from ainter.io.cmd.visualize_command import VisualizeCommand


def create_program_parser() -> ArgumentParser:
    """Creates the main program parser for the command line arguments"""

    parser = ArgumentParser()
    subparsers = parser.add_subparsers(help='List of possible subcommands',
                                       required=True)
    serve_command = ServeCommand()
    serve_command_parser = serve_command.configure_parser(subparsers)
    serve_command_parser.set_defaults(func=serve_command)

    create_model_command = CreateModelCommand()
    create_model_parser = create_model_command.configure_parser(subparsers)
    create_model_parser.set_defaults(func=create_model_command)

    visualize_command = VisualizeCommand()
    visualize_command_parser = visualize_command.configure_parser(subparsers)
    visualize_command_parser.set_defaults(func=visualize_command)
    
    return parser
