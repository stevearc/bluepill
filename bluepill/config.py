import json
import logging
import os
from typing import Any, Dict

logger = logging.getLogger(__name__)


class Config:
    def __init__(self, default_image: str = "ubuntu:latest"):
        self.default_image = default_image

    @staticmethod
    def get_config_file() -> str:
        config_dir = os.environ.get(
            "XDG_CONFIG_HOME", os.path.join(os.environ.get("HOME", "/"), ".config")
        )
        return os.path.join(config_dir, "bluepill.json")

    @staticmethod
    def get_cache_dir() -> str:
        config_dir = os.environ.get(
            "XDG_CACHE_HOME", os.path.join(os.environ.get("HOME", "/"), ".cache")
        )
        return os.path.join(config_dir, "bluepill")

    @staticmethod
    def get_cache_file(file: str) -> str:
        rel = os.path.relpath(os.path.abspath(file), "/")
        return os.path.join(Config.get_cache_dir(), rel)

    @classmethod
    def load(cls) -> "Config":
        file = cls.get_config_file()
        if not os.path.exists(file):
            return cls()
        with open(file, "r") as ifile:
            try:
                return cls(**json.load(ifile))
            except json.JSONDecodeError:
                logger.exception("Error loading config file %s", file)
                return cls()

    def asdict(self) -> Dict[str, Any]:
        return {"default_image": self.default_image}

    def save(self) -> None:
        file = self.get_config_file()
        dir = os.path.dirname(file)
        os.makedirs(dir, exist_ok=True)
        with open(file, "w") as ofile:
            json.dump(self.asdict(), ofile)
