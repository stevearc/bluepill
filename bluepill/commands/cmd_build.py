import enum
from argparse import ArgumentParser
from typing import Any

import dockerpty
from docker import DockerClient

from ..config import Config
from ..util import confirm, prompt_list
from .base import Command


class Choice(enum.Enum):
    CANCEL = enum.auto()
    REPLACE = enum.auto()
    EDIT = enum.auto()


class BuildCmd(Command):
    def __init__(
        self,
        client: DockerClient,
        config: Config,
        name: str = None,
        image: str = "",
        edit: bool = False,
        replace: bool = False,
        **kwargs: Any,
    ):
        super().__init__(client, config, **kwargs)
        self._image_name = self.get_unique_dir_name(name)
        self._hostname = self.get_hostname(name)
        self._source_image = image
        self._edit = edit
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
            "-e",
            "--edit",
            action="store_true",
            help="Enter image for editing after creation. If named image already exists, enter it for editing.",
        )
        parser.add_argument(
            "-r",
            "--replace",
            action="store_true",
            help="If named image already exists, replace it",
        )

    def run(self) -> None:
        if self.has_image(self._image_name):
            if not self._edit and not self._replace:
                choice = prompt_list(
                    f"Image '{self._image_name}' already exists:",
                    [
                        (Choice.CANCEL, "cancel"),
                        (Choice.REPLACE, "replace"),
                        (Choice.EDIT, "edit"),
                    ],
                    Choice.CANCEL,
                )
                if choice == Choice.CANCEL:
                    return
                elif choice == Choice.EDIT:
                    self._edit = True
                elif choice == Choice.REPLACE:
                    self._replace = True

        if self._replace:
            self.add_user_to_image(self._source_image, self._image_name)

        if self._edit:
            print("Customize your image. Type 'exit' when done")
            container = self.create_container(
                self._image_name,
                None,
                self._hostname,
            )
            try:
                dockerpty.start(self.client.api, container.name)
                if confirm("Commit container changes?"):
                    container.commit(tag=self._image_name)
            finally:
                container.remove(force=True)
