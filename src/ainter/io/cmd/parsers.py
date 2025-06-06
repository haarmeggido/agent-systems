from argparse import ArgumentParser

from ainter.io.cmd.visualize_command import VisualizeCommand


def create_program_parser() -> ArgumentParser:
    """Creates the main program parser for the command line arguments"""

    parser = ArgumentParser()
    subparsers = parser.add_subparsers(help='List of possible subcommands',
                                       required=True)

    visualize_command = VisualizeCommand()
    visualize_command_parser = visualize_command.configure_parser(subparsers)
    visualize_command_parser.set_defaults(func=visualize_command)
    
    return parser
