import sys
from argparse import ArgumentParser
from typing import Any, Optional

from docker import DockerClient

from ..config import Config
from .base import Command


class CommitCmd(Command):
    def __init__(
        self,
        client: DockerClient,
        config: Config,
        name: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(client, config, **kwargs)
        self._container_name = self.get_unique_dir_name(name)
        self._image_name = self.get_unique_dir_name(name)

    @classmethod
    def name(cls) -> str:
        return "commit"

    @classmethod
    def description(cls) -> str:
        return "Commit bluepill container to image"

    @classmethod
    def configure(cls, config: Config, parser: ArgumentParser) -> None:
        parser.add_argument(
            "name",
            nargs="?",
            help="Name of the container/image (if omitted, will use a unique name generated from the current directory)",
        )

    def run(self) -> None:
        container = self.get_container(self._container_name)
        if container is None:
            sys.stderr.write(f"Container {self._container_name} not found\n")
            return
        container.commit(*self._image_name.split(":"))
        print(f"Committed changes to {self._image_name}")
