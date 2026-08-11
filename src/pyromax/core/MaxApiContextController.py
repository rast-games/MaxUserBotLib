from __future__ import annotations
from typing import Any, TYPE_CHECKING

from typing_extensions import Self

from pydantic import BaseModel, PrivateAttr

if TYPE_CHECKING:
    from .client import MaxApi


class ContextController(BaseModel):
    """Base model that can be bound to a MaxApi instance."""

    _max_api: MaxApi | None = PrivateAttr()

    def model_post_init(self, __context: Any) -> None:
        """Store the bot instance from Pydantic context if present.

        :param __context: Pydantic validation context.
        :type __context: Any
        """
        self._max_api = __context.get("max_api") if __context else None

    def as_(self, max_api: MaxApi | None) -> Self:
        """Bind object to a bot instance.

        :param max_api: MaxApi instance.
        :type max_api: MaxApi | None

        :returns: Self with bound bot.
        :rtype: Self
        """
        self._max_api = max_api
        return self

    @property
    def bot(self) -> MaxApi | None:
        """Return the bound bot instance.

        :returns: The resulting MaxApi | None value.
        :rtype: MaxApi | None
        """
        return self._max_api

    @property
    def max_api(self) -> MaxApi:
        """Max api.

        :returns: The resulting MaxApi value.
        :rtype: MaxApi
        :raises RuntimeError: If object not linked to MaxApi instance.
        """
        if self._max_api is None:
            raise RuntimeError(
                f"MaxApi instance has not been bound to {self.__class__.__name__} object."
            )
        return self._max_api
