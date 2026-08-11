from __future__ import annotations

from collections.abc import Sequence, Callable
from typing import Any, overload
import functools


from .base import MiddlewareType, MiddlewareEventType, NextMiddlewareType

from ..event.UpdateType import MaxObject


class MiddlewareManager(Sequence[MiddlewareType[MaxObject]]):
    def __init__(self) -> None:
        """Initialize the middleware manager.
        """
        self._middlewares: list[MiddlewareType[MaxObject]] = []

    def register(
        self,
        middleware: MiddlewareType[MaxObject],
    ) -> MiddlewareType[MaxObject]:
        """Register.

        :param middleware: MiddlewareType[MaxObject] instance to process.
        :type middleware: MiddlewareType[MaxObject]
        :returns: The resulting MiddlewareType[MaxObject] value.
        :rtype: MiddlewareType[MaxObject]
        """
        self._middlewares.append(middleware)
        return middleware

    def unregister(self, middleware: MiddlewareType[MaxObject]) -> None:
        """Unregister.

        :param middleware: MiddlewareType[MaxObject] instance to process.
        :type middleware: MiddlewareType[MaxObject]
        """
        self._middlewares.remove(middleware)

    def __call__(
        self,
        middleware: MiddlewareType[MaxObject] | None = None,
    ) -> (
        Callable[[MiddlewareType[MaxObject]], MiddlewareType[MaxObject]]
        | MiddlewareType[MaxObject]
    ):
        """Invoke the middleware manager.

        :param middleware: MiddlewareType[MaxObject] instance to process.
        :type middleware: MiddlewareType[MaxObject] | None
        :returns: The resulting Callable[[MiddlewareType[MaxObject]], MiddlewareType[MaxObject]] | MiddlewareType[MaxObject] value.
        :rtype: Callable[[MiddlewareType[MaxObject]], MiddlewareType[MaxObject]] | MiddlewareType[MaxObject]
        """
        if middleware is None:
            return self.register
        return self.register(middleware)

    @overload
    def __getitem__(self, item: int) -> MiddlewareType[MaxObject]:
        """Getitem.

        :param item: The item value.
        :type item: int
        :returns: The resulting MiddlewareType[MaxObject] value.
        :rtype: MiddlewareType[MaxObject]
        """
        pass

    @overload
    def __getitem__(self, item: slice) -> Sequence[MiddlewareType[MaxObject]]:
        """Getitem.

        :param item: slice instance to process.
        :type item: slice
        :returns: The resulting collection.
        :rtype: Sequence[MiddlewareType[MaxObject]]
        """
        pass

    def __getitem__(
        self,
        item: int | slice,
    ) -> MiddlewareType[MaxObject] | Sequence[MiddlewareType[MaxObject]]:
        """Getitem.

        :param item: int | slice instance to process.
        :type item: int | slice
        :returns: The resulting MiddlewareType[MaxObject] | Sequence[MiddlewareType[MaxObject]] value.
        :rtype: MiddlewareType[MaxObject] | Sequence[MiddlewareType[MaxObject]]
        """
        return self._middlewares[item]

    def __len__(self) -> int:
        """Len.

        :returns: The resulting int value.
        :rtype: int
        """
        return len(self._middlewares)

    @staticmethod
    def wrap_middlewares(
        middlewares: Sequence[MiddlewareType[MiddlewareEventType]],
        handler: Callable[..., Any],
    ) -> NextMiddlewareType[MiddlewareEventType]:

        """Wrap middlewares.

        :param middlewares: Collection of middlewares.
        :type middlewares: Sequence[MiddlewareType[MiddlewareEventType]]
        :param handler: Handler to invoke.
        :type handler: Callable[..., Any]
        :returns: The resulting NextMiddlewareType[MiddlewareEventType] value.
        :rtype: NextMiddlewareType[MiddlewareEventType]
        """
        middleware = handler
        for m in reversed(middlewares):
            middleware = functools.partial(m, middleware)
        return middleware
