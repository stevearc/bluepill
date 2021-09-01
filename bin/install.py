#!/usr/bin/env python
import sys

if sys.version_info < (3, 6):
    raise Exception("bluepill requires python 3.6+")

import argparse
import os
import shutil
import subprocess
import tarfile
import tempfile
import venv
from contextlib import contextmanager
from typing import Iterator
from urllib.request import urlretrieve


def main() -> None:
    """Main method"""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        "ref",
        nargs="?",
        help="Branch, tag, or ref to install (default %(default)s)",
        default="master",
    )
    parser.add_argument(
        "-d",
        "--dest",
        help="Where to put the binary (default %(default)s)",
        default=os.curdir,
    )
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tempdir:
        with tempfile.TemporaryDirectory() as venv_dir:
            build_exe(args.ref, venv_dir, tempdir, args.dest)


@contextmanager
def pushd(dest: str) -> Iterator[None]:
    start = os.getcwd()
    os.chdir(dest)
    try:
        yield
    finally:
        os.chdir(start)


def build_exe(ref: str, venv_dir: str, workdir: str, dest: str) -> None:
    print("Downloading bluepill")
    url = f"https://github.com/stevearc/bluepill/archive/{ref}.tar.gz"
    bundle = urlretrieve(url)[0]
    with pushd(workdir):
        shutil.move(bundle, "bluepill.tar.gz")
        with tarfile.open("bluepill.tar.gz", "r:gz") as tar:
            package_dir = tar.next()
            if package_dir is None:
                raise Exception("Downloaded github archive is malformed")
            tar.extractall()
    bluepill = os.path.join(workdir, package_dir.name)

    print("Creating virtualenv")
    venv.create(venv_dir, with_pip=True)
    pip = os.path.join(venv_dir, "bin", "pip")
    subprocess.check_call([pip, "install", "pex", "wheel"])
    pex = os.path.join(venv_dir, "bin", "pex")
    print("Building executable")
    exe = os.path.join(dest, "bluepill")
    subprocess.check_call(
        [pex, "setuptools", bluepill, "-m", "bluepill:main", "-o", exe]
    )
    print(f"executable written to {exe}")


if __name__ == "__main__":
    main()
