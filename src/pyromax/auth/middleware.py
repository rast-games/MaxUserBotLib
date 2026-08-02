from collections.abc import Callable, Awaitable
from abc import abstractmethod
from typing import Any

from ..dispatcher.middlewares.base import AbstractMiddleware
from ..models.AuthFlow import AuthFlow


class BaseAuthMiddleware(
    AbstractMiddleware[AuthFlow[Any, Any, Any], AuthFlow[Any, Any, Any]]
):
    @abstractmethod
    async def __call__(
        self,
        handler: Callable[
            [AuthFlow[Any, Any, Any], dict[type[Any] | str, Any]], Awaitable[Any]
        ],
        event: AuthFlow[Any, Any, Any],
        data: dict[type[Any] | str, Any],
    ) -> Any: ...
