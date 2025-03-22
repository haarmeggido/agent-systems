from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace


class CMDCommand(ABC):

    @abstractmethod
    def configure_parser(self, subparser) -> ArgumentParser:
        pass

    @abstractmethod
    def __call__(self, args: Namespace) -> None:
        pass
