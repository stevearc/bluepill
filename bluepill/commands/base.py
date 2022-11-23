import getpass
import hashlib
import os
import sys
from abc import ABC, abstractmethod
from argparse import ArgumentParser
from io import BytesIO
from typing import Any, Dict, List, Optional, Sequence, Type, cast

from docker import DockerClient
from docker.errors import ContainerError, NotFound
from docker.models.containers import Container
from docker.models.images import Image

from ..config import Config

if sys.version_info < (3, 8):
    from typing_extensions import TypedDict
else:
    from typing import TypedDict


class Volume(TypedDict):
    bind: str
    mode: str


class ContainerArgs(TypedDict):
    environment: Dict[str, str]
    stdin_open: bool
    tty: bool
    user: str
    group_add: List[int]
    userns_mode: str
    volumes: Dict[str, Volume]
    working_dir: str


def add_parser_commands(
    parser: ArgumentParser,
    config: Config,
    commands: Sequence[Type["Command"]],
    command_name: str,
    default_command: Optional[Type["Command"]] = None,
) -> None:
    if default_command is not None:
        parser.set_defaults(**{command_name: default_command})
    subparsers = parser.add_subparsers()
    for command in commands:
        subparser = subparsers.add_parser(
            command.name(),
            description=command.description(),
            aliases=command.aliases(),
        )
        command.configure(config, subparser)
        subparser.set_defaults(**{command_name: command})


class Command(ABC):
    def __init__(self, client: DockerClient, config: Config, **kwargs: Any):
        self._kwargs = kwargs
        self.client = client
        self.config = config

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        raise NotImplementedError

    @classmethod
    def aliases(cls) -> Sequence[str]:
        return ()

    @classmethod
    @abstractmethod
    def description(cls) -> str:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def configure(cls, config: Config, parser: ArgumentParser) -> None:
        raise NotImplementedError

    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError

    def get_hostname(self, name: Optional[str] = None) -> str:
        if name is not None:
            return name
        return os.path.basename(os.path.abspath(os.getcwd()))

    def get_unique_dir_name(self, name: Optional[str] = None) -> str:
        if name is not None:
            return name
        curdir = os.path.realpath(os.path.abspath(os.getcwd()))
        md5 = hashlib.md5()
        md5.update(curdir.encode("utf-8"))
        return f"bluepill-{os.path.basename(curdir)}-{md5.hexdigest()}"

    def has_image(self, name: str) -> bool:
        include_version = ":" in name
        images = self.client.images.list()
        for image in images:
            image = cast(Image, image)
            if image.id == name:
                return True
            for tag in image.tags:
                if include_version and name == tag:
                    return True
                elif not include_version and name == tag.split(":")[0]:
                    return True
        return False

    def get_container(self, name: str) -> Optional[Container]:
        try:
            return cast(Container, self.client.containers.get(name))
        except NotFound:
            return None

    def add_user_to_image(self, source_image: str, dest_image: str) -> None:
        uid = os.getuid()
        gid = os.getgid()
        user = getpass.getuser()
        if not self.has_image(source_image):
            self.client.images.pull(*source_image.split(":"))
        try:
            stdout = (
                self.client.containers.run(
                    source_image, f"-u {user}", entrypoint="id", remove=True
                )
                .decode("utf-8")
                .strip()
            )
        except ContainerError:
            has_user = False
        else:
            has_user = stdout == str(uid)

        if has_user:
            text = BytesIO(f"FROM {source_image}".encode("utf-8"))
        else:
            text = BytesIO(
                f"""FROM {source_image}
RUN apt-get update -q && \
  apt-get install -y -q sudo && \
  groupadd -g {gid} {user} && \
  useradd -m -u {uid} -g {gid} -s /bin/bash {user} && \
  echo "{user} ALL = (ALL) NOPASSWD: ALL" >> /etc/sudoers.d/user
ENTRYPOINT ["/bin/bash", "-l"]
""".encode(
                    "utf-8"
                )
            )
        self.client.images.build(fileobj=text, tag=dest_image)

    def create_container(
        self, image: str, name: Optional[str], hostname: str, mount: bool = False
    ) -> Container:
        if name is not None:
            try:
                container = cast(Container, self.client.containers.get(name))
            except NotFound:
                pass
            else:
                container.remove()
        args = self.get_container_args(mount)
        container = self.client.containers.create(
            image,
            "-l",
            name=name,
            hostname=hostname,
            entrypoint="/bin/bash",
            **args,
        )
        return cast(Container, container)

    def get_container_args(self, mount: bool = False) -> ContainerArgs:
        user = getpass.getuser()
        environment = {"USER": user}
        volumes: Dict[str, Volume] = {}
        ssh_auth_sock = os.environ.get("SSH_AUTH_SOCK")
        home = os.environ.get("HOME", "/")
        id_rsa = os.path.join(home, ".ssh", "id_rsa")
        if ssh_auth_sock:
            environment["SSH_AUTH_SOCK"] = "/ssh-agent"
            volumes[ssh_auth_sock] = {
                "bind": "/ssh-agent",
                "mode": "rw",
            }
        elif os.path.exists(id_rsa):
            volumes[id_rsa] = {
                "bind": id_rsa,
                "mode": "ro",
            }
            id_rsa_pub = id_rsa + ".pub"
            volumes[id_rsa_pub] = {
                "bind": id_rsa_pub,
                "mode": "ro",
            }
        working_dir = home
        if mount:
            here = os.path.abspath(os.curdir)
            working_dir = os.path.join(home, os.path.basename(here))
            volumes[here] = {
                "bind": working_dir,
                "mode": "rw",
            }
        return {
            "environment": environment,
            "stdin_open": True,
            "tty": True,
            "user": user,
            "group_add": [os.getgid()],
            "userns_mode": "host",
            "volumes": volumes,
            "working_dir": working_dir,
        }
