import argparse
import logging
import sys

import docker

from .commands import HelpCmd, add_parser_commands, all_commands
from .config import Config


def _setup_logging(args: argparse.Namespace) -> None:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(levelname)s %(asctime)s [%(name)s] %(message)s")
    handler.setFormatter(formatter)
    logging.root.addHandler(handler)
    level = logging.getLevelName(args.log_level)
    logging.root.setLevel(level)


def main() -> None:
    """Create and manage per-directory docker images and containers"""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        "--log-level",
        type=lambda l: logging.getLevelName(l.upper()),
        default=logging.WARNING,
        help="Stdout logging level (default 'warning')",
    )
    parser.set_defaults(root_parser=parser)
    config = Config.load()
    add_parser_commands(parser, config, all_commands, "command", HelpCmd)
    args = parser.parse_args()
    _setup_logging(args)

    client = docker.from_env(timeout=360)
    cmd = args.command(client, config, **vars(args))
    cmd.run()


if __name__ == "__main__":
    main()
