from argparse import ArgumentParser
from typing import Any

import dockerpty
from docker import DockerClient

from ..config import Config
from .base import Command


class EnterCmd(Command):
    def __init__(
        self,
        client: DockerClient,
        config: Config,
        name: str = None,
        image: str = "",
        **kwargs: Any,
    ):
        super().__init__(client, config, **kwargs)
        self._container_name = self.get_unique_dir_name(name)
        self._image_name = self.get_unique_dir_name(name)
        self._hostname = self.get_hostname(name)
        self._source_image = image

    @classmethod
    def name(cls) -> str:
        return "enter"

    @classmethod
    def description(cls) -> str:
        return "Interactively run the docker container"

    @classmethod
    def configure(cls, config: Config, parser: ArgumentParser) -> None:
        parser.add_argument(
            "name",
            nargs="?",
            help="Name of the container/image (if omitted, will use a unique name generated from the current directory)",
        )
        parser.add_argument(
            "-i",
            "--image",
            help="Source image to use if image is not created yet (default %(default)s)",
            default=config.default_image,
        )

    def run(self) -> None:
        container = self.get_container(self._container_name)
        if container is None:
            if not self.has_image(self._image_name):
                self.add_user_to_image(self._source_image, self._image_name)
            container = self.create_container(
                self._image_name, self._container_name, self._hostname, True
            )
        dockerpty.start(self.client.api, container.name)
