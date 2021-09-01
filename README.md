# Bluepill

A command line utility for working inside docker containers.

## Why would you want to use this?

The main feature of bluepill is that it lets you easily enter a docker container
as your own user. This allows you to modify files on your host system without
messing up ownership/permissions, but any software you install is isolated
within the container.

* You want to compile a project from source, but don't want to install all the
    build dependencies on your host system
* You want to run tests for a project, but don't want to install all the test
    dependencies on your system (e.g. 5 different python versions)

## Quick Start

Download and run the install script
```sh
curl -o install.py https://raw.githubusercontent.com/stevearc/bluepill/master/bin/install.py \
  && python install.py
```

This will create a standalone `bluepill` executable that you can install
anywhere on your system. Run `bluepill --help` or `bluepill help <cmd>` for
information on how to use it.

Here's an example from one of my common usage patterns. This builds an image for
the directory with many versions of python. I can then use `tox` to run tests
across all those versions.

```sh
user@host:~$ cd myproject
user@host:~/myproject$ bluepill build -i fkrull/multi-python
user@host:~/myproject$ bluepill enter
user@myproject:~/myproject$ tox
```

## What if I need multiple containers?

If you need multiple containers so that you can run associated services (e.g.
redis, memcached, etc.), this goes beyond the scope of `bluepill`. This is a job
for [docker-compose](https://docs.docker.com/compose/).
