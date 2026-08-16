from collections.abc import Callable
from typing import TypeVar, Any

T = TypeVar("T")


def hide_func_call(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """Uses to hide function call from static analyzer."""

    return func(*args, **kwargs)
