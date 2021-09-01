from typing import List, Type

from .base import Command
from .base import add_parser_commands as add_parser_commands
from .cmd_build import BuildCmd
from .cmd_commit import CommitCmd
from .cmd_config import ConfigCmd
from .cmd_delete import DeleteCmd
from .cmd_enter import EnterCmd
from .cmd_help import HelpCmd as HelpCmd

__all__ = ["all_commands"]

all_commands: List[Type[Command]] = [
    BuildCmd,
    ConfigCmd,
    HelpCmd,
    DeleteCmd,
    EnterCmd,
    CommitCmd,
]
