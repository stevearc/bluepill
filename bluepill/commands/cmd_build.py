from argparse import ArgumentParser
from typing import Any, Optional

from docker import DockerClient

from ..config import Config
from ..util import confirm
from .base import Command


class BuildCmd(Command):
    def __init__(
        self,
        client: DockerClient,
        config: Config,
        name: Optional[str] = None,
        image: str = "",
        replace: bool = False,
        **kwargs: Any,
    ):
        super().__init__(client, config, **kwargs)
        self._image_name = self.get_unique_dir_name(name)
        self._hostname = self.get_hostname(name)
        self._source_image = image
        self._replace = replace

    @classmethod
    def name(cls) -> str:
        return "build"

    @classmethod
    def description(cls) -> str:
        return "Build a docker image"

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
            default=config.default_image,
            help="Source image to use (default %(default)s)",
        )
        parser.add_argument(
            "-r",
            "--replace",
            action="store_true",
            help="If named image already exists, replace it",
        )

    def run(self) -> None:
        if self.has_image(self._image_name) and not confirm(
            f"Image '{self._image_name}' already exists:", False
        ):
            return
        self.add_user_to_image(self._source_image, self._image_name)
