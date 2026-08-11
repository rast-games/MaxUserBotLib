import abc
from typing import TypeVar, Generic, Any

from pydantic import BaseModel

from ..core.MaxApiContextController import ContextController

T = TypeVar("T", bound=Any)


class BaseMaxApiMethod(ContextController, BaseModel, Generic[T], abc.ABC):

    @abc.abstractmethod
    async def __call__(self, *args: Any, **kwargs: Any) -> T | Any:
        """Execute the base max api MAX API method.

        :param args: Positional arguments forwarded to the wrapped callable.
        :type args: Any
        :param kwargs: Keyword arguments forwarded to the wrapped callable.
        :type kwargs: Any
        :returns: The resulting T | Any value.
        :rtype: T | Any
        """
        pass
