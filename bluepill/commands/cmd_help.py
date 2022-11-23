from argparse import ArgumentParser
from typing import Any, Optional

from docker import DockerClient

from ..config import Config
from .base import Command


class HelpCmd(Command):
    def __init__(
        self,
        client: DockerClient,
        config: Config,
        root_parser: ArgumentParser,
        cmd: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(client, config, **kwargs)
        self._parser = root_parser
        self._command = cmd

    @classmethod
    def name(cls) -> str:
        return "help"

    @classmethod
    def description(cls) -> str:
        return "Print help information about a command"

    @classmethod
    def configure(cls, config: Config, parser: ArgumentParser) -> None:
        parser.add_argument("cmd", nargs="?", help="Print help for this command")

    def run(self) -> None:
        if self._command is None:
            self._parser.print_help()
        else:
            self._parser.parse_args([self._command, "-h"])
