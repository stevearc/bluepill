from argparse import ArgumentParser
from typing import Any

from docker import DockerClient

from ..config import Config
from .base import Command, add_parser_commands


class ConfigCmd(Command):
    @classmethod
    def name(cls) -> str:
        return "config"

    @classmethod
    def description(cls) -> str:
        return "Get or set config values"

    @classmethod
    def configure(cls, config: Config, parser: ArgumentParser) -> None:
        add_parser_commands(
            parser,
            config,
            [ConfigListCmd, ConfigGetCmd, ConfigSetCmd],
            "command",
        )

    def run(self) -> None:
        cmd = ConfigListCmd(self.client, self.config, **self._kwargs)
        cmd.run()


class ConfigListCmd(Command):
    @classmethod
    def name(cls) -> str:
        return "list"

    @classmethod
    def description(cls) -> str:
        return "List config values"

    @classmethod
    def configure(cls, config: Config, parser: ArgumentParser) -> None:
        pass

    def run(self) -> None:
        for key, val in self.config.asdict().items():
            print(f"{key}: {val}")


class ConfigGetCmd(Command):
    def __init__(
        self,
        client: DockerClient,
        config: Config,
        key: str,
        **kwargs: Any,
    ):
        super().__init__(client, config, **kwargs)
        self._key = key

    @classmethod
    def name(cls) -> str:
        return "get"

    @classmethod
    def description(cls) -> str:
        return "Get config value"

    @classmethod
    def configure(cls, config: Config, parser: ArgumentParser) -> None:
        parser.add_argument(
            "key",
            help="Config key to fetch",
        )

    def run(self) -> None:
        print(str(self.config.asdict()[self._key]))


class ConfigSetCmd(Command):
    def __init__(
        self,
        client: DockerClient,
        config: Config,
        key: str,
        value: str,
        **kwargs: Any,
    ):
        super().__init__(client, config, **kwargs)
        self._key = key
        self._value = value

    @classmethod
    def name(cls) -> str:
        return "set"

    @classmethod
    def description(cls) -> str:
        return "Set config value"

    @classmethod
    def configure(cls, config: Config, parser: ArgumentParser) -> None:
        parser.add_argument(
            "key",
            help="Config key to set",
        )
        parser.add_argument("value", help="New config value")

    def run(self) -> None:
        setattr(self.config, self._key, self._value)
        self.config.save()
