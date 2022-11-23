from argparse import ArgumentParser
from typing import Any, Optional

from docker import DockerClient

from ..config import Config
from .base import Command


class DeleteCmd(Command):
    def __init__(
        self,
        client: DockerClient,
        config: Config,
        name: Optional[str] = None,
        i: bool = False,
        force: bool = False,
        **kwargs: Any,
    ):
        super().__init__(client, config, **kwargs)
        self._container_name = self.get_unique_dir_name(name)
        self._image_name = self.get_unique_dir_name(name)
        self._del_image = i
        self._force = force

    @classmethod
    def name(cls) -> str:
        return "rm"

    @classmethod
    def description(cls) -> str:
        return "Delete bluepill container or image"

    @classmethod
    def configure(cls, config: Config, parser: ArgumentParser) -> None:
        parser.add_argument(
            "name",
            nargs="?",
            help="Name of the container/image (if omitted, will use a unique name generated from the current directory)",
        )
        parser.add_argument("-i", action="store_true", help="Delete the image as well")
        parser.add_argument("-f", "--force", action="store_true", help="Force delete")

    def run(self) -> None:
        container = self.get_container(self._container_name)
        if container is not None:
            container.remove(force=self._force)
            print(f"Deleted container {container.name}")
        if self._del_image:
            if self.has_image(self._image_name):
                self.client.images.remove(self._image_name, force=self._force)
                print(f"Deleted image {self._image_name}")
