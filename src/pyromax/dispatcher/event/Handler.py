from __future__ import annotations

from collections.abc import Callable
from typing import Any, TYPE_CHECKING, Generic, Optional, TypeVar, Mapping
from dataclasses import dataclass
import logging
import inspect


from ..ObserverPattern import Observer
from ...utils import inspect_and_form
from ...filters.magic import MagicFilter

from .UpdateType import UNHANDLED, ResolvedUpdate, MaxObject
from ...filters import Filter


from magic_filter.magic import MagicFilter as OriginalMagicFilter


if TYPE_CHECKING:
    from ...models import DataDict
    from ...models import BaseMaxObject


f = TypeVar('f', bound=Filter | Callable[[MaxObject, Mapping[Any, Any]], Any])

@dataclass
class FilterObject(Generic[f]):
    filter: f
    magic: Optional[OriginalMagicFilter | MagicFilter] = None

    def __post_init__(self):
        self.resolve = self._resolve
        self.awaitable = inspect.isawaitable(self.filter) or inspect.iscoroutinefunction(self.filter)
        if isinstance(self.filter, OriginalMagicFilter):
            self.magic = self.filter
            self.resolve = self._magic_resolve

            if not isinstance(self.magic, MagicFilter):
                logging.getLogger('Magic Filter').info(
                    msg="You are using F provided by magic_filter package directly, "
                    "but it lacks `_SKIP_CHECK_PREPARATIONS: bool = True` and \n"
                    " `async def _check(self, update, *args: Any, **kwargs: Any) -> bool: return self.resolve(update)` extension."
                    "\n Please change the import statement: from `from magic_filter import F` "
                    "to `from pyromax import F` to silence this warning.",
                    stacklevel=6
                )
        if isinstance(self.filter, Filter):
            self.awaitable = True


    async def _magic_resolve(self, update: ResolvedUpdate, *args: Any) -> Any:
        self.magic: MagicFilter
        return self.magic.resolve(update)


    async def _resolve(self, update: ResolvedUpdate, data: dict[Any, Any]) -> bool | dict[str, Any]:
        assert not isinstance(self.filter, MagicFilter)
        if self.awaitable:
            return await self.filter(update, data)
        return self.filter(update, data)


    async def __call__(self, update: ResolvedUpdate, data: dict[Any, Any], *args: Any, **kwargs: Any) -> Any:
        return await self.resolve(update, data)


class Handler(Observer, Generic[ResolvedUpdate]):
    """Wrap a callable handler with filters and a pattern."""
    def __init__(self, function: Callable[..., Any], filters: list[FilterObject], pattern: Callable[[ResolvedUpdate], Any] | None = None):
        """Create a handler wrapper.

        Parameters
        ----------
        function
            Async callable to execute.
        filters
            Iterable of filters to apply before calling the handler.
        pattern
            Optional predicate used as a final condition.
        """
        self.function = function
        self.filters = filters
        self.pattern = pattern
        self.function = function


    async def _propagate_update(self, update: ResolvedUpdate, data: dict[Any, Any]) -> bool:
        if self.pattern is None and not self.filters:
            return True
        for f in self.filters:
            check = await f(update, data=data)
            if isinstance(check, dict):
                data.update(check)
            if not check:
                return False
        if self.pattern is not None:
            return bool(self.pattern(update))
        return True


    async def check(self, update: ResolvedUpdate, data: dict[Any, Any]) -> bool:
        return await self._propagate_update(update, data)


    async def update(self, update: ResolvedUpdate, data: dict[Any, Any] | None = None) -> Any:
        if data is None:
            raise ValueError('data cannot be None')
        check = await self._propagate_update(update, data)
        if check:
            args = inspect_and_form(self.function, data)
            return await self.function(**args)
        return UNHANDLED


    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} filters={self.filters}> pattern={self.pattern}>>'

