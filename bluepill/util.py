from typing import Any, Callable, List, Tuple, TypeVar, cast

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


def prompt_list(text: str, choices: List[Tuple[T, str]], default: T = None) -> T:
    """Prompt the user to choose one of a list of options"""
    while True:
        for i, [_, option] in enumerate(choices):
            print("[%d] %s" % (i + 1, option))
        response = prompt(text, default="__none__")
        if default is not None and response == "__none__":
            return default
        try:
            idx = int(response) - 1
            if 0 <= idx < len(choices):
                return choices[idx][0]
        except (ValueError, IndexError):
            pass
        print("Invalid choice\n")


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
