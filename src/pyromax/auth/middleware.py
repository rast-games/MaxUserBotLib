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
    ) -> Any:
        """Process an event through the base auth middleware.

        :param handler: Handler to invoke.
        :type handler: Callable[[AuthFlow[Any, Any, Any], dict[type[Any] | str, Any]], Awaitable[Any]]
        :param event: Incoming event to process.
        :type event: AuthFlow[Any, Any, Any]
        :param data: Contextual data passed through the processing pipeline.
        :type data: dict[type[Any] | str, Any]
        :returns: The value returned by the wrapped callable or backend.
        :rtype: Any
        """
        ...
