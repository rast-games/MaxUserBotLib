from collections.abc import Callable, Coroutine
from typing import Any, cast

from .Base import BaseMaxApiMethod
from ..models import TwoFactorAction

NoneType = type(None)


class Remove2FaMethod(BaseMaxApiMethod[NoneType]):
    async def __call__(
        self,
        password: str,
        two_factor_actions: list[TwoFactorAction] | None = None,
        remove_2fa: bool = True,
    ) -> None:
        if not self._max_api:
            raise RuntimeError("Remove2Fa method not bound to MaxApi instance")
        return cast(
            None,
            await self._max_api.mapper.call_method(
                type(self),
                password=password,
                expected_capabilities=two_factor_actions,
                remove_2fa=remove_2fa,
            ),
        )
