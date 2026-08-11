from logging import Logger
from typing import Protocol, Any

from ...methods import BaseMaxApiMethod


class CoreMixinsProtocol(Protocol):

    async def __call__(
        self, class_of_method: type[BaseMaxApiMethod[Any]], *args: Any, **kwargs: Any
    ) -> Any: ...

    _logger: Logger | None
