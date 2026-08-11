from typing import NoReturn


class SkipHandler(Exception):
    pass


class CancelHandler(Exception):
    pass


def skip(message: str | None = None) -> NoReturn:
    """Raise an SkipHandler

    :param message: The message value.
    :type message: str | None
    :raises SkipHandler: If the requested action cannot be completed.
    """
    raise SkipHandler(message or "Event skipped")
