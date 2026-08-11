from __future__ import annotations

from typing import Any, TYPE_CHECKING, cast

from .base import Filter
from ..models import BaseMaxObject

from magic_filter import MagicFilter as _MagicFilter

if TYPE_CHECKING:
    from ..dispatcher.event import ResolvedUpdate


class AlwaysEqual:
    def __eq__(self, other: Any) -> bool:
        """Eq.

        :param other: The other value.
        :type other: Any
        :returns: True when the requested condition is satisfied; otherwise False.
        :rtype: bool
        """
        return True


class MagicFilter(_MagicFilter, Filter):  # type: ignore[misc]
    _SKIP_CHECK_PREPARATIONS: bool = True

    @property
    def work_with(self) -> tuple[type[BaseMaxObject]]:
        """Work with.

        :returns: The resulting tuple[type[BaseMaxObject]] value.
        :rtype: tuple[type[BaseMaxObject]]
        """
        return cast(tuple[type[BaseMaxObject]], (AlwaysEqual(),))

    async def _check(self, update: ResolvedUpdate, *args: Any, **kwargs: Any) -> Any:
        """Check.

        :param update: Incoming update to process.
        :type update: ResolvedUpdate
        :param args: Positional arguments forwarded to the wrapped callable.
        :type args: Any
        :param kwargs: Keyword arguments forwarded to the wrapped callable.
        :type kwargs: Any
        :returns: The value returned by the wrapped callable or backend.
        :rtype: Any
        """
        return self.resolve(update)


F = MagicFilter()
