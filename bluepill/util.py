from typing import Any, Callable, TypeVar, cast

NO_DEFAULT = object()

T = TypeVar("T")


def prompt(
    msg: str,
    default: str = cast(Any, NO_DEFAULT),
    validate: Callable[[str], bool] = None,
) -> str:
    """Prompt user for input"""
    while True:
        response = input(msg + " ").strip()
        if not response:
            if default is NO_DEFAULT:
                continue
            return default
        if validate is None or validate(response):
            return response


def confirm(msg: str, default: bool = None) -> bool:
    """Display a blocking prompt until the user confirms"""
    while True:
        yes = "Y" if default else "y"
        if default or default is None:
            no = "n"
        else:
            no = "N"
        response = prompt("%s [%s/%s]" % (msg, yes, no), "").lower()
        if response in ("y", "yes"):
            return True
        elif response in ("n", "no"):
            return False
        elif not response and default is not None:
            return default
