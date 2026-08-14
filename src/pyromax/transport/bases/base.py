from typing import Any, TypeVar, Generic
from abc import abstractmethod

from ...mixins import AsyncInitializerMixin, AsyncConstructorMeta
from ...encoding import BaseEncoding

ENCODING_TYPE = TypeVar("ENCODING_TYPE", bound=BaseEncoding[Any, Any])


class BaseTransport(AsyncInitializerMixin, Generic[ENCODING_TYPE]):
    BASE_EXCEPTION_FOR_TRANSPORT: type[Exception]

    OTHER_EXCEPTIONS_FOR_TRANSPORT: list[type[Exception]]

    @abstractmethod
    async def _async_init(
        self,
        encoding: ENCODING_TYPE,
        *args: Any,
        **kwargs: Any,
    ) -> Any: ...

    @abstractmethod
    def __init__(
        self,
        encoding: ENCODING_TYPE,
        *args: Any,
        **kwargs: Any,
    ) -> None: ...
